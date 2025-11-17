# handlers/anonymous_chat.py
"""
Handlers and logic for random anonymous chat matching.

Main features:
  - Users can join a queue based on their own gender and preferred partner gender.
  - When two compatible users are found, they are connected in an anonymous chat.
  - Inactivity timeout (5 minutes) automatically ends inactive chats.
  - Users can end the chat, search for a new partner, or cancel search.
"""

import asyncio
from typing import Dict, Set, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from loader import bot
from config import config
from keyboards.random_chat_kb import random_chat_keyboard
from keyboards.main_menu import main_menu_keyboard
from services.antispam import check_spam

router = Router()

# Texts used in the main menu for anonymous chat buttons.
SEARCH_TEXT = "💬 چت ناشناس"
NEXT_TEXT = "⏭ بعدی"
END_TEXT = "❌ پایان چت"

# Anonymous chat state structures
# user_id -> "male" / "female"
user_gender: Dict[int, str] = {}

# user_id -> "male" / "female" / "any"
user_target_gender: Dict[int, str] = {}

# Users waiting for a random partner
random_waiting: Set[int] = set()

# user_id -> partner_id
random_partner: Dict[int, int] = {}

# user_id -> background search task
random_search_tasks: Dict[int, asyncio.Task] = {}

# frozenset({user_id, partner_id}) -> inactivity timer task
random_inactivity_tasks: Dict[frozenset[int], asyncio.Task] = {}


def get_partner(user_id: int) -> Optional[int]:
    """
    Return the partner_id for the given user_id, if any.
    """
    return random_partner.get(user_id)


def _make_gender_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting the user's own gender.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="پسر 🚹", callback_data="rand_self_male"),
                InlineKeyboardButton(text="دختر 🚺", callback_data="rand_self_female"),
            ]
        ]
    )


def _make_target_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting the desired partner's gender.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="به پسر وصل شم 🚹", callback_data="rand_target_male"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="به دختر وصل شم 🚺", callback_data="rand_target_female"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="فرقی نمی‌کنه 🎲", callback_data="rand_target_any"
                ),
            ],
        ]
    )


def _make_cancel_search_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard with a single button to cancel the search.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="لغو جستجو ❌", callback_data="rand_cancel_search"
                )
            ]
        ]
    )


async def can_match(user1: int, user2: int) -> bool:
    """
    Check if two users can be matched based on their genders and preferences.
    """
    g1 = user_gender.get(user1)
    g2 = user_gender.get(user2)
    t1 = user_target_gender.get(user1, "any")
    t2 = user_target_gender.get(user2, "any")

    if not g1 or not g2:
        return False

    ok1 = (t1 == "any" or g2 == t1)
    ok2 = (t2 == "any" or g1 == t2)

    return ok1 and ok2


async def reset_inactivity_timer(u1: int, u2: int) -> None:
    """
    Reset the inactivity timer for an active chat between u1 and u2.

    If there is no activity for 5 minutes, the chat will be ended.
    """
    chat_key = frozenset({u1, u2})
    old = random_inactivity_tasks.get(chat_key)
    if old:
        old.cancel()

    async def timer():
        try:
            await asyncio.sleep(300)  # 5 minutes inactivity timeout
            if random_partner.get(u1) == u2 and random_partner.get(u2) == u1:
                try:
                    await bot.send_message(
                        u1, "⏰ به دلیل ۵ دقیقه عدم فعالیت، مکالمه قطع شد."
                    )
                except Exception:
                    pass
                try:
                    await bot.send_message(
                        u2, "⏰ به دلیل ۵ دقیقه عدم فعالیت، مکالمه قطع شد."
                    )
                except Exception:
                    pass
                random_partner.pop(u1, None)
                random_partner.pop(u2, None)
        finally:
            random_inactivity_tasks.pop(chat_key, None)

    random_inactivity_tasks[chat_key] = asyncio.create_task(timer())


async def end_chat(user_id: int, reason_for_self: Optional[str] = None) -> None:
    """
    End the anonymous chat for the given user_id and notify both users.
    """
    partner = random_partner.get(user_id)
    if not partner:
        return

    # Remove chat relation
    random_partner.pop(user_id, None)
    random_partner.pop(partner, None)

    chat_key = frozenset({user_id, partner})
    t = random_inactivity_tasks.pop(chat_key, None)
    if t:
        t.cancel()

    # Notify both users
    try:
        await bot.send_message(
            user_id,
            reason_for_self or "مکالمه قطع شد.",
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        pass

    try:
        await bot.send_message(
            partner,
            "مکالمه توسط طرف مقابل قطع شد.",
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        pass


async def start_random_search(user_id: int, chat_id: int) -> None:
    """
    Put the user into the matching queue or match them with a waiting partner.
    """
    # If already in a chat, do not start a new search
    if user_id in random_partner:
        await bot.send_message(
            chat_id,
            "الان در حال چت با یک ناشناس هستی 🗣️\n"
            "اگه می‌خوای مکالمه فعلی رو تموم کنی، از دکمه «❌ پایان چت» "
            "یا دستور /cancel استفاده کن.",
            reply_markup=random_chat_keyboard(),
        )
        return

    # Remove previous waiting state and cancel previous search timer if any
    if user_id in random_waiting:
        random_waiting.discard(user_id)
    t_old = random_search_tasks.pop(user_id, None)
    if t_old:
        t_old.cancel()

    # Try to find a partner from the current waiting list
    for other_id in list(random_waiting):
        if await can_match(user_id, other_id):
            random_waiting.discard(other_id)
            t2 = random_search_tasks.pop(other_id, None)
            if t2:
                t2.cancel()

            random_partner[user_id] = other_id
            random_partner[other_id] = user_id

            kb = random_chat_keyboard()

            await bot.send_message(
                user_id,
                "✅ به یک ناشناس وصل شدی!\n"
                "هر پیامی اینجا بفرستی به صورت ناشناس برای طرف مقابل ارسال می‌شه.",
                reply_markup=kb,
            )
            await bot.send_message(
                other_id,
                "✅ به یک ناشناس وصل شدی!\n"
                "هر پیامی اینجا بفرستی به صورت ناشناس برای طرف مقابل ارسال می‌شه.",
                reply_markup=kb,
            )

            await reset_inactivity_timer(user_id, other_id)
            return

    # No partner found → add to waiting queue
    random_waiting.add(user_id)
    await bot.send_message(
        chat_id,
        "🔍 در حال جستجو برای یک ناشناس مناسب...\n"
        "تا ۵ دقیقه اگر کسی پیدا نشه، عملیات لغو می‌شه.",
        reply_markup=_make_cancel_search_keyboard(),
    )

    async def search_timer():
        try:
            await asyncio.sleep(300)
            if user_id in random_waiting and user_id not in random_partner:
                random_waiting.discard(user_id)
                await bot.send_message(
                    chat_id,
                    "⏰ تو این بازه زمانی کسی برای چت پیدا نشد.\n"
                    "می‌تونی بعداً دوباره امتحان کنی.",
                    reply_markup=main_menu_keyboard(),
                )
        finally:
            random_search_tasks.pop(user_id, None)

    random_search_tasks[user_id] = asyncio.create_task(search_timer())


# ------------- Entry point from main menu -------------


@router.message(F.text == SEARCH_TEXT)
async def start_anon_flow(message: Message) -> None:
    """
    Entry point for the random anonymous chat from the main menu.

    If the user is already in a chat, just remind them. Otherwise, ask for gender.
    """
    user_id = message.from_user.id

    if user_id in random_partner:
        await message.answer(
            "الان در حال چت با یک ناشناس هستی ✅\n"
            "برای پایان چت از دکمه‌ی «❌ پایان چت» استفاده کن.",
            reply_markup=random_chat_keyboard(),
        )
        return

    await message.answer(
        "جنسیت خودت رو انتخاب کن:",
        reply_markup=_make_gender_keyboard(),
    )


# ------------- Step 1: select own gender -------------


@router.callback_query(F.data == "rand_self_male")
async def self_male(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_gender[user_id] = "male"

    await callback.message.answer(
        "می‌خوای به چه کسی وصل بشی؟",
        reply_markup=_make_target_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "rand_self_female")
async def self_female(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_gender[user_id] = "female"

    await callback.message.answer(
        "می‌خوای به چه کسی وصل بشی؟",
        reply_markup=_make_target_keyboard(),
    )
    await callback.answer()


# ------------- Step 2: select target gender -------------


@router.callback_query(F.data == "rand_target_male")
async def target_male(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_target_gender[user_id] = "male"
    await start_random_search(user_id, callback.message.chat.id)
    await callback.answer()


@router.callback_query(F.data == "rand_target_female")
async def target_female(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_target_gender[user_id] = "female"
    await start_random_search(user_id, callback.message.chat.id)
    await callback.answer()


@router.callback_query(F.data == "rand_target_any")
async def target_any(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_target_gender[user_id] = "any"
    await start_random_search(user_id, callback.message.chat.id)
    await callback.answer()


# ------------- Cancel search via button -------------


@router.callback_query(F.data == "rand_cancel_search")
async def cancel_search_cb(callback: CallbackQuery) -> None:
    """
    Cancel the anonymous chat search if the user is in the waiting queue.
    """
    user_id = callback.from_user.id

    if user_id in random_waiting:
        random_waiting.discard(user_id)
        t = random_search_tasks.pop(user_id, None)
        if t:
            t.cancel()
        await callback.message.answer(
            "جستجوی چت ناشناس لغو شد ✅",
            reply_markup=main_menu_keyboard(),
        )
    elif user_id in random_partner:
        await callback.message.answer(
            "الان به یه ناشناس وصل شدی 😊\n"
            "اگه می‌خوای همین مکالمه رو قطع کنی، از دکمه «❌ پایان چت» استفاده کن "
            "یا دستور /cancel رو بفرست.",
            reply_markup=random_chat_keyboard(),
        )
    else:
        await callback.message.answer(
            "در حال حاضر در صف جستجوی چت ناشناس نیستی 🙂",
            reply_markup=main_menu_keyboard(),
        )

    await callback.answer()


# ------------- "End chat" and "Next" buttons -------------


@router.message(F.text == END_TEXT)
async def end_chat_cmd(message: Message) -> None:
    """
    Handle the "end chat" button from the user.
    """
    user_id = message.from_user.id
    if user_id not in random_partner:
        await message.answer(
            "در حال حاضر در چت ناشناسی نیستی.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await end_chat(user_id, "مکالمه رو قطع کردی.")


@router.message(F.text == NEXT_TEXT)
async def next_chat(message: Message) -> None:
    """
    Handle the "next" button.

    Ends the current chat (if any) and starts a new search.
    """
    user_id = message.from_user.id

    if user_id in random_partner:
        await end_chat(
            user_id,
            "مکالمه قبلی تموم شد، دنبال یه ناشناس جدید می‌گردم...",
        )

    await start_anon_flow(message)


# ------------- /cancel and /cansel commands -------------


@router.message(Command("cancel", "cansel"))
async def cancel_handler(message: Message) -> None:
    """
    Handle /cancel and /cansel commands.

    Stops search or ends active chat, if any.
    """
    user_id = message.from_user.id
    cancelled_any = False

    if user_id in random_waiting:
        random_waiting.discard(user_id)
        t = random_search_tasks.pop(user_id, None)
        if t:
            t.cancel()
        await message.answer("جستجوی چت ناشناس لغو شد ✅")
        cancelled_any = True

    if user_id in random_partner:
        await end_chat(user_id, "مکالمه رو لغو کردی.")
        cancelled_any = True

    if not cancelled_any:
        await message.answer("فعلاً فرایند فعالی نداری که لغوش کنم 🙂")
    else:
        await message.answer(
            "همه فرایندهای فعال متوقف شدند ✅",
            reply_markup=main_menu_keyboard(),
        )


# ------------- Forward messages while in anonymous chat -------------


@router.message(lambda m: get_partner(m.from_user.id) is not None)
async def handle_chat_message(message: Message) -> None:
    """
    Handle messages while the user is in an anonymous chat session.
    """
    user_id = message.from_user.id
    partner_id = get_partner(user_id)

    if not partner_id:
        return

    # Simple anti-spam check
    if check_spam(user_id):
        await message.answer("⏳ کمی آهسته‌تر پیام بده، لطفاً.")
        return

    # Log messages to the log channel if configured
    try:
        if config.LOG_CHANNEL_ID is not None:
            await message.forward(chat_id=config.LOG_CHANNEL_ID)
    except Exception:
        pass

    # Copy the message to the partner, preserving anonymity
    try:
        await message.copy_to(chat_id=partner_id)
    except Exception:
        await message.answer("⚠️ مشکلی در ارسال پیام به ناشناس پیش آمد.")

    # Reset inactivity timer on each message
    await reset_inactivity_timer(user_id, partner_id)
