# Nashenas Telegram Bot

Persian anonymous chat & message Telegram bot built with **Aiogram 3** and **webhooks**.

این ربات امکان چت و پیام ناشناس بین کاربران تلگرام را فراهم می‌کند؛ هم به صورت چت رندوم با ناشناس، هم ارسال پیام ناشناس با لینک اختصاصی، و هم پیام به «مخاطب خاص».

---

## Features

- 💬 **چت ناشناس رندوم**
  - اتصال تصادفی دو کاربر بر اساس جنسیت خود و جنسیت موردنظر
  - تایمر عدم فعالیت (۵ دقیقه) و قطع خودکار مکالمه
  - دکمه‌های «⏭ بعدی» و «❌ پایان چت»

- 📨 **لینک پیام ناشناس**
  - تولید لینک اختصاصی برای هر کاربر (`/start <user_id>`)
  - صف پیام‌های ناشناس و دریافت با دستورات `/newms` و `/newmsg`
  - پاسخ ناشناس با ریپلای روی پیام‌های دریافتی

- 🎯 **پیام به مخاطب خاص**
  - کاربر می‌تواند با وارد کردن `@username` یا `user_id` پیام ناشناس برای یک فرد مشخص بفرستد
  - بررسی می‌شود که مخاطب حداقل یک‌بار `/start` را زده باشد

- ℹ️ **راهنما و قوانین**
  - متن راهنما و قوانین استفاده از ربات به صورت دکمه در منوی اصلی

- 🗂 **ساختار ماژولار**
  - `handlers/` برای هندلرها
  - `database/` (SQLite)
  - `services/` (logger, antispam, text utils, matchmaking, ...)
  - `states/` (FSM)
  - `keyboards/` (Reply keyboards)

---

## Tech Stack

- Python 3.10+
- [Aiogram 3](https://docs.aiogram.dev/)
- Aiohttp (Webhook server)
- SQLite (لوکال و ساده، بدون نیاز به سرور دیتابیس جدا)

---

## Project Structure

```text
nashenas-telegram-bot/
    main.py               # aiohttp webhook entrypoint
    config.py             # config loader (from environment variables)
    loader.py             # Bot & Dispatcher initialization

    handlers/             # all bot handlers (start, anonymous chat, messages, help, special contact)
    database/             # db.py (SQLite schema + helpers)
    services/             # logger, antispam, text utils, matchmaking, user utils, ...
    keyboards/            # main menu and random chat keyboards
    states/               # aiogram FSM states
