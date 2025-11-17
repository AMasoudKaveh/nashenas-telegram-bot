# handlers/start.py
"""
Handlers for the /start command.

- Registers the user in the database.
- If a deep-link payload is provided (/start <user_id>), it will
  set up an anonymous messaging session with the target user.
"""

from aiogram import Router, types
from aiogram.filters import CommandStart

from keyboards.main_menu import main_menu_keyboard
from database.db import add_user
from loader import bot
from handlers.anonymous_message import active_targets  # tracks active anonymous targets

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    """
    Handle the /start command with optional payload.

    - /start                 → show main menu
    - /start <user_id:int>   → start anonymous message session with that user
    """
    user = message.from_user

    # Ensure the user is registered in the database
    add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    parts = message.text.split(maxsplit=1)
    payload = parts[1] if len(parts) > 1 else None

    # No payload → show main menu
    if not payload:
        await message.answer(
            "سلام 👋\n"
            "به برنامه ناشناس خوش آمدی.\n\n"
            "از منوی زیر انتخاب کن:",
            reply_markup=main_menu_keyboard(),
        )
        return

    # Non-numeric payload → treat like a normal /start
    if not payload.isdigit():
        await message.answer(
            "سلام 👋\n"
            "برای استفاده از ربات از منوی زیر یکی رو انتخاب کن:",
            reply_markup=main_menu_keyboard(),
        )
        return

    target_id = int(payload)

    # User opened their own link
    if target_id == user.id:
        await message.answer(
            "این لینک متعلق به خودته 😊\n"
            "برای دریافت پیام ناشناس از بقیه، همین لینک رو برای دیگران بفرست.",
            # You can uncomment this if you want to always show the main menu here:
            # reply_markup=main_menu_keyboard(),
        )
        return

    # User came from someone else's link and wants to send an anonymous message
    active_targets[user.id] = target_id

    # Try to resolve a human-friendly name for the target user
    try:
        chat = await bot.get_chat(target_id)
        target_name = (
            getattr(chat, "full_name", None)
            or getattr(chat, "first_name", None)
            or getattr(chat, "username", None)
            or "این کاربر"
        )
    except Exception:
        target_name = "این کاربر"

    await message.answer(
        "سلام 👋\n"
        f"شما در حال پیام دادن به «{target_name}» هستین.\n\n"
        "هر پیامی اینجا بفرستی به صورت ناشناس براش ارسال می‌شه 🕵️‍♂️",
    )
