import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from states.states import FSMStates
from survey import questions, visualize_answers

import typing

from aiogram import Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from lexicon.lexicon import LEXICON_RU


rt = Router()
lexicon = LEXICON_RU


@rt.message(CommandStart())
async def prepare_user(msg: Message, state: FSMContext):
    await msg.answer(lexicon["start"])
    await state.set_state(FSMStates.entering_name)
    data = {"answers": {category: {} for category in questions.QUESTION_CATEGORIES}}
    await state.set_data(data)
    

@rt.message(StateFilter(FSMStates.entering_name))
async def set_name_and_start_survey(msg: Message, state: FSMContext):
    data = await state.get_data()
    data["name"] = msg.text
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
        await visualize_answers.finish_and_send_results(clb.message, state)