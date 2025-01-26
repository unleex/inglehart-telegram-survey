import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from states.states import FSMStates
from survey import questions, visualize_answers

import asyncio
import typing

from aiogram import Router
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from lexicon.lexicon import LEXICON_RU


rt = Router()
lexicon = LEXICON_RU
DATABASE_PATH = os.path.join("database", "database.json")
MAX_NAME_LENGTH = 20


@rt.message(CommandStart())
async def prepare_user(msg: Message, state: FSMContext):
    await msg.answer(lexicon["start"])
    await state.set_state(FSMStates.entering_name)
    data = {"answers": {category: {} for category in questions.QUESTION_CATEGORIES}}
    await state.set_data(data)
    

@rt.message(StateFilter(FSMStates.entering_name))
async def set_name_and_start_survey(msg: Message, state: FSMContext):
    data = await state.get_data()
    data["name"] = msg.text[:20]
    data["username"] = msg.from_user.username
    data["user_id"] = msg.from_user.id
    data["current_question_idx"] = 0

    await state.set_data(data)
    await msg.answer(lexicon["start_survey"] % data["name"])

    await questions.ask_question(
        msg.chat.id, 
        questions.QUESTIONS[data["current_question_idx"]], 
        questions.ANSWERS, 
        state
        )
    data = await state.get_data()
    await state.set_data(data)


@rt.callback_query(StateFilter(FSMStates.answering))
async def get_answer_and_ask_new(
    clb: CallbackQuery, 
    state: FSMContext, 
    ):
    await clb.message.delete()
    data = await state.get_data()
    await questions.get_answer(
        question=questions.Question(data["text"], data["category"]), 
        answer_value=int(clb.data), 
        state=state
        )
    data = await state.get_data()
    if data["current_question_idx"] < len(questions.QUESTIONS):
        question = questions.QUESTIONS[data["current_question_idx"]]
        await questions.ask_question(clb.message.chat.id, question, questions.ANSWERS, state)
    else:
        x_pos, y_pos = await visualize_answers.finish_and_send_results(clb.message, state)
        visualize_answers.save_results_to_db(
            database_path=DATABASE_PATH,
            x_pos=x_pos,
            y_pos=y_pos,
            name=data["name"],
            username=data["username"],
            user_id=data["user_id"]
        )
        await state.clear()


@rt.message(Command("user_map"), StateFilter(default_state))
async def user_map_and_fellow_suggestions(msg: Message, state: FSMContext):
    user_map_path, fellow_report_message = visualize_answers.get_user_map_and_fellow_suggestion(
        msg.from_user.id, DATABASE_PATH
    )
    user_map = FSInputFile(user_map_path)
    await msg.answer_photo(user_map, fellow_report_message)
    await asyncio.sleep(visualize_answers.IMAGE_REMOVAL_TIMEOUT)
    os.remove(user_map_path)
