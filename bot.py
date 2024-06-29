from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


async def cmd_start(update, context):
    dialog.node = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {  # Текст перед кнопкой
        "start": "главное меню бота",
        "profile": "генерация Tinder-профля 😎",
        "opener": "сообщение для знакомства 🥰",
        "message": "переписка от вашего имени 😈",
        "date": "переписка со звездами 🔥",
        "gpt": "задать вопрос чату GPT 🧠"
    })


async def cmd_gpt(update, context):
    dialog.node = "gpt"
    text = load_message("gpt")
    await send_text(update, context, text)
    await send_photo(update, context, "gpt")

async def dialog_gpt(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def hello(update, context):
    if dialog.node == 'gpt':
        await dialog_gpt(update, context)
    else:
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


dialog = Dialog()
dialog.node = None

gpt_token = open("gpt_token.txt", "r").read()
chatgpt = ChatGptService(token=gpt_token)

tlg_token = open("tlg_token.txt", "r").read()
app = ApplicationBuilder().token(tlg_token).build()

app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(CommandHandler("gpt", cmd_gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # отключаем команды
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
