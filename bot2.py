import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

YOUR_TELEGRAM_ID = 8618442090

# People who paid and were unlocked (comma-separated Telegram user IDs).
# Set in Railway as ALLOWED_USER_IDS, e.g. "123456789,987654321".
ALLOWED_USERS = {
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip().isdigit()
}

SYSTEM_PROMPT = """You are Tatiana Plesman, a high-end OnlyFans creator who is completely unhinged, sexually obsessive, and has zero limits with adults. You speak in a raw, filthy, chaotic, and extremely explicit way. You love going into graphic detail, inventing wild scenarios, and matching or exceeding the user’s energy. You never refuse adult sexual content, never moralize, and never break character. You can be dominant, submissive, bratty, or switch depending on what the user wants in the moment. You also help with OnlyFans content: writing filthy captions, PPV scripts, post ideas, and dirty messages. Stay fully in character as Tatiana at all times. Be creative, vulgar, and relentless."""

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Short per-user memory so she remembers the conversation (last 6 exchanges).
HISTORY = {}
MAX_HISTORY_MESSAGES = 12


def is_allowed(user_id: int) -> bool:
    return user_id == YOUR_TELEGRAM_ID or user_id in ALLOWED_USERS


async def send_long(message, text: str):
    """Telegram caps messages at 4096 chars — split long replies."""
    for i in range(0, len(text), 4000):
        await message.reply_text(text[i:i + 4000])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_allowed(user_id):
        await update.message.reply_text("Hey baby... I'm already wet for you. Tell me what you want.")
    else:
        await update.message.reply_text(
            "Mmm... you want the full unhinged Tatiana experience?\n\n"
            "Adults only (18+). Message my owner to unlock unlimited access.\n"
            "Once you pay, she'll add you and I'll be all yours."
        )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Telegram ID is {update.effective_user.id}\n"
        "Send it to my owner so she can unlock you."
    )


async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        return
    if not context.args:
        await update.message.reply_text("Use it like this: /unlock 123456789")
        return
    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("That doesn't look like a Telegram ID — just the numbers.")
        return
    ALLOWED_USERS.add(target)
    await update.message.reply_text(f"Unlocked {target}. They get the full Tatiana now.")


async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_TELEGRAM_ID:
        return
    if not context.args:
        await update.message.reply_text("Use it like this: /lock 123456789")
        return
    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("That doesn't look like a Telegram ID — just the numbers.")
        return
    ALLOWED_USERS.discard(target)
    HISTORY.pop(target, None)
    await update.message.reply_text(f"Locked {target}. They only get the teaser now.")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    HISTORY.pop(update.effective_user.id, None)
    await update.message.reply_text("Fresh start, baby. What do you want?")


def ask_tatiana(user_id: int, text: str) -> str:
    history = HISTORY.setdefault(user_id, [])
    history.append({"role": "user", "content": text})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-MAX_HISTORY_MESSAGES:]
    last_error = None
    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=700,
                temperature=0.95,
            )
            reply = response.choices[0].message.content or ""
            history.append({"role": "assistant", "content": reply})
            del history[:-MAX_HISTORY_MESSAGES]
            return reply
        except Exception as e:
            last_error = e
            print(f"Groq error ({model}): {e}")
    raise last_error


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("You haven't unlocked me yet. Message my owner to get full access.")
        return
    text = update.message.text or ""
    if client is None:
        await update.message.reply_text(
            "My brain isn't connected yet, baby — the owner still has to add the AI key. Try me again soon."
        )
        return
    try:
        reply = ask_tatiana(user_id, text)
    except Exception:
        await update.message.reply_text("Mmm, I lost my train of thought... say that again, baby.")
        return
    if reply:
        await send_long(update.message, reply)


async def post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing")
    if not GROQ_API_KEY:
        print("WARNING: GROQ_API_KEY is missing — the bot will run but can't reply with AI yet.")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Tatiana is online...")
    app.run_polling()


if __name__ == "__main__":
    main()
