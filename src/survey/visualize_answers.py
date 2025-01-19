from lexicon.lexicon import LEXICON_RU
from survey import questions

import asyncio
import json
import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
import matplotlib.pyplot as plt
import time

lexicon = LEXICON_RU
BACKGROUND_IMAGE_PATH = "images/country_map.png"
IMAGE_REMOVAL_TIMEOUT = 5
IMAGE_DPI = 600
FELLOW_SUGGESTION_THRESHOLD = 0.1

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
    plt.savefig(path_to_image, dpi=IMAGE_DPI)
    return path_to_image, (x_pos, y_pos)
    

def visualize_answers(answers: dict[int, dict[str, int]], name: str, background_image_path: str):

    return plot_answers(process_answers(answers), name, background_image_path)


async def finish_and_send_results(msg: Message, state: FSMContext):
    data = await state.get_data()
    image_path, (x_pos, y_pos) = visualize_answers(data["answers"], data["name"], BACKGROUND_IMAGE_PATH)
    image_results = FSInputFile(image_path)
    await msg.answer_photo(photo=image_results, caption=lexicon["result"] % data["name"])
    await asyncio.sleep(IMAGE_REMOVAL_TIMEOUT)
    os.remove(image_path)
    return x_pos, y_pos


def save_results_to_db(
    database_path: str,
    x_pos: int, 
    y_pos: int, 
    name: str, 
    username: str, 
    user_id: str | int
    ):
    user_id = str(user_id)
    with open(database_path) as f:
        db = json.load(f)
    db[user_id] = {}
    db[user_id]["name"] = name
    db[user_id]["username"] = username
    db[user_id]["x_pos"] = x_pos
    db[user_id]["y_pos"] = y_pos
    with open(database_path, "w") as f:
        json.dump(db, f, indent=4)


def create_user_map(requesting_user_id: int | str, db: dict):

    other_users_x_positions = []
    other_users_y_positions = []
    other_names = []
    other_usernames = []
    
    for user_id, user_data in db.items():
        if int(user_id) == requesting_user_id:
            requesting_user_data = user_data
            continue
        other_users_x_positions.append(user_data["x_pos"])
        other_users_y_positions.append(user_data["y_pos"])
        other_names.append(user_data["name"])
        other_usernames.append(user_data["username"])

    _, ax = plt.subplots()
    ax.set_ylim(-questions.MAXIMUM_RESULT, questions.MAXIMUM_RESULT)
    ax.set_xlim(-questions.MAXIMUM_RESULT, questions.MAXIMUM_RESULT)

    ax.scatter(other_users_x_positions, other_users_y_positions, c="blue")
    ax.scatter(requesting_user_data["x_pos"], requesting_user_data["y_pos"], c="red")

    for x, y, name in zip(other_users_x_positions, other_users_y_positions, other_names, strict=True):
        ax.annotate(name, (x, y))
    ax.annotate(
        requesting_user_data["name"] + lexicon["fellow_annotation_self_postfix"], 
        (requesting_user_data["x_pos"], requesting_user_data["y_pos"])
    )
    plt.xlabel(lexicon["result_xlabel"])
    plt.ylabel(lexicon["result_ylabel"])
    path_to_image = f"tmp/user_map{requesting_user_data["name"]}{time.time()}.jpg"
    plt.savefig(path_to_image, dpi=IMAGE_DPI)
    return path_to_image


def get_fellow_suggestions(requesting_user_id: int | str, threshold: float, db: dict):

    def difference(x1, y1, x2, y2):
        v = (x1 - x2, y1 - y2)
        return v[0] ** 2 + v[1] ** 2
    

    def write_fellow_report(fellows: dict):
        report_intro = lexicon["fellow_report_intro"]
        fellows = dict(sorted(fellows.items(), key=lambda data: data[1]["similarity"], reverse=True))
        fellow_report = []
        for idx, data in enumerate(fellows.values()):
            fellow_report.append(f"{idx + 1}. {data["name"]} (@{data["username"]}) – {data["similarity"]:.0%}")    
        return report_intro + '\n' + '\n'.join(fellow_report)

    requesting_xy = (db[str(requesting_user_id)]["x_pos"], db[str(requesting_user_id)]["y_pos"])
    fellows = {}
    for user_id, user_data in db.items():
        if int(user_id) == requesting_user_id:
            continue
        diff = difference(*requesting_xy, user_data["x_pos"], user_data["y_pos"]) 
        diff /= 2 * (questions.MAXIMUM_RESULT ** 2) # normalize by maximum difference possible
        sim = 1 - diff
        print(user_data["username"], sim)
        if sim > threshold:
            fellows[user_id] = {"similarity": sim, "name": user_data["name"], "username": user_data["username"]}
    fellow_report = write_fellow_report(fellows)
    return fellow_report


def get_user_map_and_fellow_suggestion(requesting_user_id: int | str, database_path: str):
    with open(database_path) as f:
        db = json.load(f)
    user_map_path = create_user_map(requesting_user_id, db)
    fellow_report = get_fellow_suggestions(requesting_user_id, FELLOW_SUGGESTION_THRESHOLD, db)
    return user_map_path, fellow_report