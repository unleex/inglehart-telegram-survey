import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from keyboards.keyboards import some_keyboard
from lexicon.lexicon import LEXICON_EN
from states.states import FSMStates


rt = Router()
lexicon = LEXICON_EN


@rt.message(Command("cmd1"), StateFilter(default_state))
async def handler1(msg: Message, state: FSMContext):
    await msg.answer(lexicon["some_phrase"])
    await state.set_state(FSMStates.some_state)