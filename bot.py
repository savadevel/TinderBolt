from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


async def hello(update, context):
    await send_text(update, context, "_Привет!_")
    await send_text(update, context, "Вы написали " + update.message.text)
    await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
        "btn_start": " Старт ",  # Текст и команда кнопки "Старт"
        "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
    })
    await send_photo(update, context, "avatar_main")


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    if query == "btn_start":
        await send_text(update, context, "Вы нажали на кнопку старт")
    else:
        await send_text(update, context, "Вы нажали на кнопку стоп")


async def cmd_start(update, context):
    text = load_message("main")
    await send_text(update, context, text)
    await send_photo(update, context, "main")

token = open("token.txt", "r").read()
app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # отключаем команды
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
