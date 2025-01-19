from aiogram.types import BotCommand
from aiogram import Bot


async def set_main_menu(bot: Bot) -> None:
    main_menu_commands = [
        BotCommand(command="cmd1", description="Some command"),
        BotCommand(command="cmd2", description="Other command"),
    ]
    await bot.set_my_commands(main_menu_commands)