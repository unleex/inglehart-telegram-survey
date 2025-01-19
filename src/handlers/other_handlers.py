import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from keyboards.keyboards import some_keyboard
from lexicon.lexicon import LEXICON_EN
from states.states import FSMStates


rt = Router()
lexicon = LEXICON_EN


@rt.message(StateFilter(FSMStates.some_state))
async def handler2(msg: Message, state: FSMContext):
    await msg.answer(lexicon["other_phrase"], reply_markup=some_keyboard)
    await state.clear()