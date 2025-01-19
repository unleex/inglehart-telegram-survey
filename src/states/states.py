from aiogram.fsm.state import State, StatesGroup


class FSMStates(StatesGroup):
    entering_name = State()
    answering = State()