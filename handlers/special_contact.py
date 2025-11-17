# handlers/special_contact.py
"""
Handlers for the "special contact" feature.

Flow:
  1. User clicks the "به مخاطب خاصم وصلم کن" button.
  2. Bot asks for either @username or numeric user_id of the target.
  3. Bot checks if the target user has used the bot before (exists in DB).
  4. If valid, bot waits for the anonymous message text.
  5. The message is sent anonymously to the target user.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from loader import bot
from states.special_contact_states import SpecialContactStates
from database.db import user_exists, get_user_id_by_username

special_contact_router = Router()


# Step 1: user clicks the button
@special_contact_router.message(F.text == "به مخاطب خاصم وصلم کن")
async def special_contact_start(message: Message, state: FSMContext) -> None:
    """
    Entry point for the special contact flow.

    Asks the user to provide either a @username or a numeric user_id.
    """
    text = (
        "به مخاطب خاصت وصل می‌کنمت 😉\n\n"
        "راه اول 👈 : Username@ یا همون آی‌دی تلگرام اون شخص رو الان وارد ربات کن !\n"
        "راه دوم 👈 : آیدی‌عددی (id number) اون شخص رو الان وارد ربات کن !"
    )
    await message.answer(text)
    await state.set_state(SpecialContactStates.waiting_for_target)


# Step 2: read username or numeric ID and resolve to user_id
@special_contact_router.message(SpecialContactStates.waiting_for_target)
async def special_contact_get_target(message: Message, state: FSMContext) -> None:
    """
    Handle the user input for the special contact target.

    Accepts either:
      - A numeric user_id
      - A username or @username
    """
    raw = message.text.strip()

    target_id: int | None = None

    # Numeric input → treat as user_id
    if raw.isdigit():
        target_id = int(raw)

        if target_id == message.from_user.id:
            await message.answer(
                "🙂 خودت رو که نمی‌تونی به عنوان مخاطب خاص انتخاب کنی! یه آیدی دیگه وارد کن."
            )
            return

        if not user_exists(target_id):
            await message.answer(
                "❌ این آیدی هنوز از ربات استفاده نکرده.\n"
                "بهش بگو اول /start رو توی ربات بزنه، بعد دوباره امتحان کن."
            )
            return

    else:
        # Non-numeric input → treat as username or @username
        target_id = get_user_id_by_username(raw)

        if target_id is None:
            await message.answer(
                "❌ این Username رو توی دیتابیس پیدا نکردم.\n"
                "مطمئنی طرف یک‌بار /start رو توی ربات زده و یوزرنیمش درسته؟\n"
                "دوباره با @username یا آیدی عددی امتحان کن."
            )
            return

        if target_id == message.from_user.id:
            await message.answer(
                "🙂 خودت رو که نمی‌تونی به عنوان مخاطب خاص انتخاب کنی! یه آی‌دی دیگه وارد کن."
            )
            return

    # If we reach here, target_id is valid
    await state.update_data(target_id=target_id)
    await message.answer("✅ مخاطب پیدا شد.\nحالا پیامت رو بفرست تا ناشناس براش ارسال کنم.")
    await state.set_state(SpecialContactStates.waiting_for_message)


# Step 3: receive the message and send it anonymously
@special_contact_router.message(SpecialContactStates.waiting_for_message)
async def special_contact_send_message(message: Message, state: FSMContext) -> None:
    """
    Receive the anonymous message from the user and forward it to the target.
    """
    data = await state.get_data()
    target_id = data["target_id"]

    if not message.text:
        await message.answer("فعلاً فقط پیام متنی پشتیبانی می‌شود. لطفاً یک متن بفرست.")
        return

    out_text = (
        "📩 یک پیام ناشناس از یک مخاطب خاص دریافت کردی:\n\n"
        f"{message.text}"
    )

    try:
        await bot.send_message(chat_id=target_id, text=out_text)
    except Exception:
        await message.answer(
            "❌ نتونستم پیام رو ارسال کنم.\n"
            "ممکنه مخاطب ربات رو بلاک کرده باشه یا چت قابل دسترسی نباشه."
        )
        await state.clear()
        return

    await message.answer("✅ پیامت به صورت ناشناس برای مخاطب خاصت ارسال شد.")
    await state.clear()
