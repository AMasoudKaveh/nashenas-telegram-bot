# handlers/anonymous_message.py
"""
Handlers for the "anonymous message via link" feature.

Flow overview:
  - User requests their personal anonymous link (button "📨 پیام ناشناس"
    or inline callback "my_anon_link").
  - Other users open that link (/start <owner_id>) and send a message.
  - Messages are stored in a queue for the link owner.
  - The owner can use /newms or /newmsg to fetch queued messages.
  - Replying to those messages (via reply) sends an anonymous response
    back to the original sender.
"""

from typing import Dict, List, Any, Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from loader import bot
from config import config

router = Router()

# --------- Anonymous message data structures ---------
# anonymous_sender_id -> link_owner_id
active_targets: Dict[int, int] = {}

# link_owner_id -> queue of pending anonymous messages
pending_for_owner: Dict[int, List[Dict[str, Any]]] = {}

# message_id in link owner's chat -> anonymous sender user_id
reply_map: Dict[int, int] = {}


# =================================================================
# 0) Reply keyboard button "📨 پیام ناشناس" → generate personal link
# =================================================================


@router.message(F.text == "📨 پیام ناشناس")
async def my_anon_link_from_reply_keyboard(message: Message) -> None:
    """
    Send a personalized anonymous-message link to the user.

    This link can be shared so others can send anonymous messages to the user.
    """
    user = message.from_user
    user_id = user.id

    anon_link = f"https://t.me/{config.BOT_USERNAME}?start={user_id}"
    name = user.first_name or user.username or "من"

    text = (
        f"سلام {name} هستم ✋️\n\n"
        "لینک زیر رو لمس کن و هر حرفی که تو دلت هست یا هر انتقادی که نسبت به من داری "
        "رو با خیال راحت بنویس و بفرست. بدون اینکه از اسمت باخبر بشم پیامت به من می‌رسه. "
        "خودتم می‌تونی امتحان کنی و از بقیه بخوای راحت و ناشناس بهت پیام بفرستن، "
        "حرفای خیلی جالبی می‌شنوی! 😉\n\n"
        "👇👇\n"
        f"{anon_link}"
    )

    await message.answer(text)


# =================================================================
# 1) Inline version (if somewhere inline keyboard is still used)
# =================================================================


@router.callback_query(F.data == "my_anon_link")
async def my_anon_link_handler(callback: CallbackQuery) -> None:
    """
    Same as my_anon_link_from_reply_keyboard, but triggered from an inline button.
    """
    user = callback.from_user
    user_id = user.id

    anon_link = f"https://t.me/{config.BOT_USERNAME}?start={user_id}"
    name = user.first_name or user.username or "من"

    text = (
        f"سلام {name} هستم ✋️\n\n"
        "لینک زیر رو لمس کن و هر حرفی که تو دلت هست یا هر انتقادی که نسبت به من داری "
        "رو با خیال راحت بنویس و بفرست. بدون اینکه از اسمت باخبر بشم پیامت به من می‌رسه. "
        "خودتم می‌تونی امتحان کنی و از بقیه بخوای راحت و ناشناس بهت پیام بفرستن، "
        "حرفای خیلی جالبی می‌شنوی! 😉\n\n"
        "👇👇\n"
        f"{anon_link}"
    )

    await callback.message.answer(text)
    await callback.answer()


# =================================================================
# 2) /newms and /newmsg → fetch queued anonymous messages
# =================================================================


@router.message(Command("newms", "newmsg"))
async def new_message_handler(message: Message) -> None:
    """
    Fetch the next anonymous message from the queue for this user.

    If there is a queued message, it will be sent back to the user.
    The user can then reply to it to respond anonymously.
    """
    owner_id = message.from_user.id

    queue = pending_for_owner.get(owner_id)
    if not queue or len(queue) == 0:
        await message.answer("هیچ پیام ناشناسی در صف نداری 🙂")
        return

    # Take the first message from the queue
    data = queue.pop(0)
    if len(queue) == 0:
        pending_for_owner.pop(owner_id, None)

    anon_id = data["from_id"]
    msg_type = data.get("msg_type", "text")
    text = data.get("text") or ""
    file_id = data.get("file_id")

    sent_msg: Optional[Message] = None

    if msg_type == "text":
        sent_msg = await message.answer("📩 آخرین پیام ناشناس:\n\n" + (text or ""))
    elif msg_type == "photo" and file_id:
        sent_msg = await bot.send_photo(
            owner_id,
            photo=file_id,
            caption=text or "📩 پیام ناشناس (عکس)",
        )
    elif msg_type == "video" and file_id:
        sent_msg = await bot.send_video(
            owner_id,
            video=file_id,
            caption=text or "📩 پیام ناشناس (ویدیو)",
        )
    elif msg_type == "video_note" and file_id:
        sent_msg = await bot.send_video_note(owner_id, video_note=file_id)
        if text:
            await message.answer("متن همراه ویدیو مسیج:\n" + text)
    elif msg_type == "document" and file_id:
        sent_msg = await bot.send_document(
            owner_id,
            document=file_id,
            caption=text or "📩 پیام ناشناس (فایل)",
        )
    elif msg_type == "voice" and file_id:
        sent_msg = await bot.send_voice(
            owner_id,
            voice=file_id,
            caption=text or "📩 پیام ناشناس (ویس)",
        )
    elif msg_type == "audio" and file_id:
        sent_msg = await bot.send_audio(
            owner_id,
            audio=file_id,
            caption=text or "📩 پیام ناشناس (صوت)",
        )
    else:
        sent_msg = await message.answer(
            "📩 آخرین پیام ناشناس (نوع ناشناخته یا بدون مدیا):\n\n" + (text or "بدون متن"),
        )

    # Track which anonymous user sent this message so reply can be routed
    if sent_msg:
        reply_map[sent_msg.message_id] = anon_id

    await message.answer(
        "می‌تونی همینجا جواب بدی، جوابت به صورت ناشناس براش ارسال می‌شه ✅"
    )


# =================================================================
# 3) When someone sends a message via a link → enqueue for /newms
# =================================================================


@router.message(lambda m: m.from_user.id in active_targets)
async def handle_anon_sender(message: Message) -> None:
    """
    Handle messages coming from a deep-link (/start <owner_id>).

    The message is stored in the owner's queue and a notification is sent.
    """
    anon_id = message.from_user.id
    owner_id = active_targets.pop(anon_id, None)

    if not owner_id:
        return

    # Log incoming anonymous message in the log channel (if configured)
    try:
        if config.LOG_CHANNEL_ID is not None:
            await message.forward(chat_id=config.LOG_CHANNEL_ID)
    except Exception:
        # Logging is non-critical, ignore failures
        pass

    # Detect message type and file_id
    msg_type = "text"
    text = message.text or message.caption or ""
    file_id: Optional[str] = None

    if message.photo:
        msg_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        msg_type = "video"
        file_id = message.video.file_id
    elif getattr(message, "video_note", None):
        msg_type = "video_note"
        file_id = message.video_note.file_id
    elif message.document:
        msg_type = "document"
        file_id = message.document.file_id
    elif message.voice:
        msg_type = "voice"
        file_id = message.voice.file_id
    elif message.audio:
        msg_type = "audio"
        file_id = message.audio.file_id

    # Enqueue the message for the owner
    pending_for_owner.setdefault(owner_id, []).append(
        {
            "from_id": anon_id,
            "msg_type": msg_type,
            "text": text,
            "file_id": file_id,
        }
    )

    # Notify the owner about a new anonymous message
    try:
        await bot.send_message(
            owner_id,
            "📬 شما یک پیام ناشناس جدید دارید !\n\n"
            "جهت دریافت کلیک کنید 👈 /newms",
        )
    except Exception:
        # Owner might have blocked the bot or is unreachable
        pass

    # Confirm to the anonymous sender
    await message.answer(
        "پیامت به صورت ناشناس ارسال شد ✅\n\n"
        "اگه می‌خوای تو هم لینک ناشناس خودت رو داشته باشی، "
        "از منوی اصلی روی «📨 پیام ناشناس» بزن."
    )


# =================================================================
# 4) Reply to an anonymous message by replying to the /newms output
# =================================================================


@router.message(
    lambda m: m.reply_to_message
    and m.reply_to_message.message_id in reply_map
)
async def reply_to_anon(message: Message) -> None:
    """
    Handle replies to messages that came from /newms or /newmsg.

    The reply is forwarded as an anonymous message back to the original sender.
    """
    owner_id = message.from_user.id
    anon_id = reply_map.get(message.reply_to_message.message_id)
    if not anon_id:
        await message.answer("نمی‌تونم گیرنده ناشناس این پیام رو پیدا کنم 😅")
        return

    # After the reply is used once, remove the mapping to avoid misrouting
    reply_map.pop(message.reply_to_message.message_id, None)

    # Log the response in the log channel (if configured)
    try:
        if config.LOG_CHANNEL_ID is not None:
            await message.forward(chat_id=config.LOG_CHANNEL_ID)
    except Exception:
        pass

    text = message.text or message.caption or ""

    # Forward the reply to the anonymous sender, preserving media if present
    if message.photo:
        await bot.send_photo(
            anon_id,
            photo=message.photo[-1].file_id,
            caption=text or None,
        )
    elif message.video:
        await bot.send_video(
            anon_id,
            video=message.video.file_id,
            caption=text or None,
        )
    elif getattr(message, "video_note", None):
        await bot.send_video_note(
            anon_id,
            video_note=message.video_note.file_id,
        )
        if text:
            await bot.send_message(anon_id, text)
    elif message.document:
        await bot.send_document(
            anon_id,
            document=message.document.file_id,
            caption=text or None,
        )
    elif message.voice:
        await bot.send_voice(
            anon_id,
            voice=message.voice.file_id,
            caption=text or None,
        )
    elif message.audio:
        await bot.send_audio(
            anon_id,
            audio=message.audio.file_id,
            caption=text or None,
        )
    else:
        await bot.send_message(
            anon_id,
            "📨 یک پاسخ ناشناس دریافت کردید:\n\n" + (text or "پیام بدون متن"),
        )

    await message.answer("پاسخت به صورت ناشناس ارسال شد ✅")
