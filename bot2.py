import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

BOT_TOKEN = os.environ.get("BOT_TOKEN")

YOUR_TELEGRAM_ID = 8618442090

SYSTEM_PROMPT = """YOUR EXISTING TATIANA PROMPT"""

model = "Qwen/Qwen2.5-7B-Instruct"
...
client = InferenceClient(
    model=model,
    token=token,
    provider="auto"
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

if not token:
    raise ValueError("HF_TOKEN is missing")

client = InferenceClient(
    token=token,
    provider="auto"
)
ALLOWED_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == YOUR_TELEGRAM_ID or user_id in ALLOWED_USERS:
        await update.message.reply_text("Hey baby... I'm Tatiana. I'm already wet for you. Tell me what you want.")
    else:
        await update.message.reply_text("Mmm... you want the full unhinged Tatiana experience?\n\nMessage my owner to unlock unlimited access.\nOnce you pay, he'll add you and I'll be all yours.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != YOUR_TELEGRAM_ID and user_id not in ALLOWED_USERS:
        await update.message.reply_text("You haven't unlocked me yet. Message my owner to get full access.")
        return
    text = update.message.text or ""
    if text.startswith("/"):
        return
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]
    try:
        response = client.chat_completion(messages=messages, max_tokens=700, temperature=0.95)
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        print(f"HF Error: {e}")

async def post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, chat))
    print("Tatiana is online...")
    app.run_polling()

if __name__ == "__main__":
    main()
