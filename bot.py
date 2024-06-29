from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


async def cmd_debug(update, context):
    if dialog.node:
        await send_text(update, context, dialog.node)
    if len(dialog.list) > 0:
        await send_text(update, context, "\n\n".join(dialog.list))


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


async def cmd_date(update, context):
    dialog.node = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande": "1. Ариана Гранде 🔥  (сложность 5/10)",
        "date_robbie": "2. Марго Робби 🔥🔥  (сложность 7/10)",
        "date_zendaya": "3. Зендея     🔥🔥🔥 (сложность 10/10)",
        "date_gosling": "4. Райан Гослинг 😎 (сложность 7/10)",
        "date_hardy": "5. Том Харди   😎😎 (сложность 10/10)"
    })


async def dialog_date(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Набирает текст...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)


async def button_date(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()

    await send_photo(update, context, query)

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def cmd_message(update, context):
    dialog.node = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Следующее сообщение",
        "message_date": "Пригласить на свидание"
    })
    dialog.list.clear()


async def dialog_message(update, context):
    text = update.message.text
    dialog.list.append(text)


async def button_message(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "Подготовка ответа...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.node == 'gpt':
        await dialog_gpt(update, context)
    elif dialog.node == 'date':
        await dialog_date(update, context)
    elif dialog.node == 'message':
        await dialog_message(update, context)
    else:
        await send_text(update, context, "_Привет!_")
        await send_text(update, context, "Вы написали " + update.message.text)
        await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
            "btn_start": " Старт ",  # Текст и команда кнопки "Старт"
            "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
        })
        await send_photo(update, context, "avatar_main")


async def button_hello(update, context):
    query = update.callback_query.data  # код кнопки
    if query == "btn_start":
        await send_text(update, context, "Вы нажали на кнопку старт")
    else:
        await send_text(update, context, "Вы нажали на кнопку стоп")


dialog = Dialog()
dialog.node = None
dialog.list = []

gpt_token = open("gpt_token.txt", "r").read()
chatgpt = ChatGptService(token=gpt_token)

tlg_token = open("tlg_token.txt", "r").read()
app = ApplicationBuilder().token(tlg_token).build()

app.add_handler(CommandHandler("debug", cmd_debug))
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(CommandHandler("gpt", cmd_gpt))
app.add_handler(CommandHandler("date", cmd_date))
app.add_handler(CommandHandler("message", cmd_message))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # отключаем команды

app.add_handler(CallbackQueryHandler(button_date, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(button_message, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(button_hello))

app.run_polling()
