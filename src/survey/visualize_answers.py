from lexicon.lexicon import LEXICON_RU
from survey import questions

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
import matplotlib.pyplot as plt
import time

lexicon = LEXICON_RU
BACKGROUND_IMAGE_PATH = "images/country_map.png"

def process_answers(answers: dict[int, dict[str, int]]):
    total_category_values = {
        category: sum(answers[category].values())
        for category in questions.QUESTION_CATEGORIES
    }
    return total_category_values


def plot_answers(total_category_values: dict[int, int], name: str, background_image_path: str):
    x_pos = total_category_values[questions.Question.CATEGORY_SELF_EXPRESSION] \
        - total_category_values[questions.Question.CATEGORY_SURVIVAL]
    y_pos = total_category_values[questions.Question.CATEGORY_RATIONALISM] \
        - total_category_values[questions.Question.CATEGORY_TRADITION]
    

    img = plt.imread(background_image_path)
    _, ax = plt.subplots()
    x_max = questions.MAXIMUM_RESULT
    y_max = questions.MAXIMUM_RESULT
    ax.imshow(img, extent=[-x_max, x_max, -y_max, y_max])
    ax.scatter([x_pos], [y_pos])
    ax.annotate(name, (x_pos, y_pos))
    plt.xlabel(lexicon["result_xlabel"])
    plt.ylabel(lexicon["result_ylabel"])
    plt.title(lexicon["result_title"])
    path_to_image = f"tmp/{name}{time.time()}.jpg"
    plt.savefig(path_to_image)
    return path_to_image
    

def visualize_answers(answers: dict[int, dict[str, int]], name: str, background_image_path: str):

    return plot_answers(process_answers(answers), name, background_image_path)


async def finish_and_send_results(msg: Message, state: FSMContext):
    data = await state.get_data()
    image_path = visualize_answers(data["answers"], data["name"], BACKGROUND_IMAGE_PATH)
    image_results = FSInputFile(image_path)
    await msg.answer_photo(photo=image_results, caption=lexicon["result"] % data["name"])