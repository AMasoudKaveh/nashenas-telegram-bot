# handlers/callbacks.py
"""
Callback query handlers for inline buttons.

Note:
These handlers assume that somewhere in the project there are inline
keyboards that send callback_data values such as:
  - "help"
  - "rules"
  - "anonymous_chat"
  - "anonymous_message"
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "help")
async def help_section(callback: CallbackQuery) -> None:
    """
    Handle the "help" callback and show a short help section.
    """
    text = (
        "📘 *راهنما*\n\n"
        "به برنامه ناشناس خوش اومدی ❤️\n\n"
        "🔹 *چت ناشناس*: تو رو با یک کاربر تصادفی وصل می‌کنه.\n"
        "🔹 *پیام ناشناس*: می‌تونی بدون مشخص شدن هویت به کسی پیام بدی.\n"
        "🔹 *قوانین*: قوانین استفاده از ربات.\n\n"
        "اگر سوالی داشتی بپرس 🌟"
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "rules")
async def rules_section(callback: CallbackQuery) -> None:
    """
    Handle the "rules" callback and show basic usage rules.
    """
    text = (
        "⚠️ *قوانین استفاده از ربات*\n\n"
        "برای حفظ امنیت کاربران:\n\n"
        "❌ ارسال پیام آزاردهنده ممنوع\n"
        "❌ ارسال محتوای غیراخلاقی ممنوع\n"
        "❌ تلاش برای شناسایی کاربر مقابل ممنوع\n"
        "❌ اسپم و تبلیغات ممنوع\n\n"
        "✔️ استفاده سالم و محترمانه باعث ادامه فعالیت شما میشه 🌱"
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "anonymous_chat")
async def start_anonymous_chat(callback: CallbackQuery) -> None:
    """
    Handle the "anonymous_chat" callback.

    The actual anonymous chat matching logic is expected to be implemented
    in a dedicated module (e.g. `anonymous_chat.py`).
    """
    await callback.message.edit_text(
        "🔍 در حال جستجو برای یک ناشناس مناسب...\n"
        "اگر تا ۵ دقیقه کسی پیدا نشد، جستجو خودکار لغو می‌شود.",
        reply_markup=None,
        parse_mode="Markdown",
    )
    # Further logic for anonymous chat should be implemented separately.
    await callback.answer()


@router.callback_query(lambda c: c.data == "anonymous_message")
async def anonymous_message_section(callback: CallbackQuery) -> None:
    """
    Handle the "anonymous_message" callback and prompt the user
    for the target identifier.
    """
    text = (
        "برای ارسال پیام ناشناس، شناسه کاربری طرف مقابل را ارسال کن.\n\n"
        "مثال:\n`@username`"
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
    )
    # Further steps for anonymous messages should be implemented separately.
    await callback.answer()
