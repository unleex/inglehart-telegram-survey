from aiogram.types import BotCommand
from aiogram import Bot
from lexicon.lexicon import LEXICON_RU


lexicon = LEXICON_RU


async def set_main_menu(bot: Bot) -> None:
    main_menu_commands = [
        BotCommand(command="start", description=lexicon["start_command_description"]),
        BotCommand(command="user_map", description=lexicon["user_map_command_description"])
    ]
    await bot.set_my_commands(main_menu_commands)