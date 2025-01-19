from config.config import bot
from states.states import FSMStates

import itertools
import typing

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext


class Question:

    CATEGORY_TRADITION = "1"
    CATEGORY_RATIONALISM = "2"
    CATEGORY_SURVIVAL = "3"
    CATEGORY_SELF_EXPRESSION = "4"             
    def __init__(
        self, 
        text: str, 
        category: typing.Literal[tuple((
            CATEGORY_TRADITION, 
            CATEGORY_RATIONALISM, 
            CATEGORY_SURVIVAL,
            CATEGORY_SELF_EXPRESSION))] #type: ignore
        ):
        self.text = text
        self.category = category
    
    def __dict__(self):
        return {"text": self.text, "category": self.category}


TRADITION_QUESTIONS_TEXTS = [
    "Историческое наследие и национальная культура должны быть защищены от влияния глобализации.",
    "Я считаю, что подчинение старшим и уважение к их мнению являются важными добродетелями.",
    "Я считаю, что государство должно  считываться с религией введении законов.",
    "Сохранение семейных ценностей важнее личной свободы в выборе образа жизни.",
    "Следование семейным традициям важно для сохранения культурной идентичности общества."
]
RATIONALISM_QUESTIONS_TEXTS = [
    "Я предпочитаю доказательства эмоциям и личным убеждениям  против рациональных аргументов.",
    "Личное развитие и самореализация важнее выполнения коллективных обязанностей.",
    "Правительство должно основывать свои решения на научных данных, а не на общественном мнении.",
    "Я легко принимаю нововведения, технологии и открытия, противоречащие традициям.",
    "Саморазвитие и образование повышает качество жизни лучше, чем поддержание хороших отношений с семьей."
]
SURVIVAL_QUESTIONS_TEXTS = [
    "Социальные изменения должны происходить только в том случае, если они не угрожают стабильности общества.",
    "Безопасность целого общества важнее, чем индивидуальные свободы граждан. ",
    "В условиях экономического кризиса  государство вправе ограничивать права человека для поддержания  порядка.",
    "Люди должны больше полагаться на коллективные усилия, чем на индивидуальные достижения, чтобы выжить в сложных условиях.",
    "В современном мире необходимо ограничивать миграцию для защиты экономической и социальной стабильности."
]
SELF_EXPRESSION_QUESTIONS_TEXTS = [
    "Толерантность к различным культурам и меньшинствам делает общество более развитым и гармоничным.",
    "Я считаю, что творчество и индивидуальность более важны, чем следования общественным ожиданиям.",
    "Я поддерживаю идеи, которые способствуют защите прав меньшинств и равенству в обществе.",
    "Возможность свободно выражать свои мысли и убеждения важнее, чем поддержание социального порядка.",
    "Каждый человек имеет право жить так, как считает нужным, даже если это противоречит общественным нормам."
]

QUESTION_CATEGORIES = [Question.CATEGORY_TRADITION,
    Question.CATEGORY_RATIONALISM,
    Question.CATEGORY_SURVIVAL,
    Question.CATEGORY_SELF_EXPRESSION
    ]


QUESTIONS = []
for questions, category in zip(
        [
            TRADITION_QUESTIONS_TEXTS,
            RATIONALISM_QUESTIONS_TEXTS,
            SURVIVAL_QUESTIONS_TEXTS,
            SELF_EXPRESSION_QUESTIONS_TEXTS
        ],
        QUESTION_CATEGORIES
    ):
    for text in questions:
        QUESTIONS.append(Question(text=text, category=category))


ANSWERS = {
    "Полностью не согласен": 0,
    "Скорее не согласен": 1,
    "Затрудняюсь ответить": 2,
    "Скорее согласен": 3,
    "Полностью согласен": 4
}

MAXIMUM_RESULT = max(ANSWERS.values()) * (len(QUESTIONS) // len(QUESTION_CATEGORIES))


async def ask_question(
    chat_id: int, 
    question: Question, 
    answers: dict[str, int], 
    state: FSMContext
    ):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=str(value))]
            for text, value in answers.items()
        ],
        resize_keyboard=True
    )
    await bot.send_message(chat_id, question.text, reply_markup=inline_kb)
    data = await state.get_data()
    data.update(vars(question)())
    data["current_question_idx"] += 1
    await state.set_data(data)
    await state.set_state(FSMStates.answering)


async def get_answer(question: Question, answer_value: int, state: FSMContext):
    data = await state.get_data()
    data["answers"][question.category][question.text] = answer_value
    await state.set_data(data)