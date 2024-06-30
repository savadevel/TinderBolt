from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


async def cmd_debug(update, context):
    if dialog.mode is not None and len(dialog.mode) > 0:
        await send_text(update, context, f"dialog.mode = {dialog.mode}")
    if len(dialog.list) > 0:
        await send_text(update, context, "dialog.list = " + "\n\n".join(dialog.list))
    if dialog.count > 0:
        await send_text(update, context, f"dialog.count = {dialog.count}")
    if bool(dialog.user):
        await send_text(update, context, "dialog.user = " + dialog_user_info_to_str(dialog.user))


async def cmd_start(update, context):
    dialog.mode = "main"
    text = load_message(dialog.mode)
    await send_photo(update, context, dialog.mode)
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
    dialog.mode = "gpt"
    text = load_message(dialog.mode)
    await send_text(update, context, text)
    await send_photo(update, context, dialog.mode)


async def dialog_gpt(update, context):
    text = update.message.text
    prompt = load_prompt(dialog.mode)
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def cmd_date(update, context):
    dialog.mode = "date"
    text = load_message(dialog.mode)
    await send_photo(update, context, dialog.mode)
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
    dialog.mode = "message"
    text = load_message(dialog.mode)
    await send_photo(update, context, dialog.mode)
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


async def cmd_profile(update, context):
    dialog.mode = "profile"
    text = load_message(dialog.mode)
    await send_photo(update, context, dialog.mode)
    await send_text(update, context, text)

    dialog.count = 0
    dialog.user.clear()

    await send_text(update, context, "Сколько Вам лет?")


async def dialog_profile(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Кем Вы работаете?")
    elif dialog.count == 2:
        dialog.user["occuration"] = text
        await send_text(update, context, "У Вас есть хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Что Вам НЕ нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt(dialog.mode)
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "Подготовка ответа...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def cmd_opener(update, context):
    dialog.mode = "opener"
    text = load_message(dialog.mode)
    await send_photo(update, context, dialog.mode)
    await send_text(update, context, text)

    dialog.count = 0
    dialog.user.clear()

    await send_text(update, context, "Имя девушки?")


async def dialog_opener(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ей лет?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцените ее внешность: 1-10 баллов?")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Кем она работает?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt(dialog.mode)
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "Подготовка ответа...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.mode == 'gpt':
        await dialog_gpt(update, context)
    elif dialog.mode == 'date':
        await dialog_date(update, context)
    elif dialog.mode == 'message':
        await dialog_message(update, context)
    elif dialog.mode == 'profile':
        await dialog_profile(update, context)
    elif dialog.mode == 'opener':
        await dialog_opener(update, context)
    else:
        await send_photo(update, context, "avatar_main")
        await send_text(update, context, "_Привет!_\nВыбери команду /start для начала...")


async def button_hello(update, context):
    query = update.callback_query.data  # код кнопки
    if query == "btn_start":
        await send_text(update, context, "Вы нажали на кнопку старт")
    else:
        await send_text(update, context, "Вы нажали на кнопку стоп")


load_dotenv()

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

chatgpt = ChatGptService(token=os.getenv('OPEN_AI_TOKEN'))
app = ApplicationBuilder().token(os.getenv('TLG_BOT_TOKEN')).build()

app.add_handler(CommandHandler("debug", cmd_debug))
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(CommandHandler("gpt", cmd_gpt))
app.add_handler(CommandHandler("date", cmd_date))
app.add_handler(CommandHandler("message", cmd_message))
app.add_handler(CommandHandler("profile", cmd_profile))
app.add_handler(CommandHandler("opener", cmd_opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))  # отключаем команды

app.add_handler(CallbackQueryHandler(button_date, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(button_message, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(button_hello))

app.run_polling()
