from dotenv import load_dotenv
from os import getenv
import sqlite3
import telebot
from datetime import datetime

# Создание клавиатуры с кнопкой присоедениться (глобально, чтобы не нужно было каждый раз создавать новую, тем самым используя больше оперативы)
keyboard = telebot.types.InlineKeyboardMarkup(
    row_width=1,
)
# Добавление в клавиатуру самой кнопки (text думаю понятно что такое, а callback_data это грубо говоря названия события нажатия на кнопку)
keyboard.add(telebot.types.InlineKeyboardButton(text="Присоединиться", callback_data="join"))

# Создание потключение к базе данных sqlite3 (она хранится в файле queue.db и через сторонний софт типо JetBrains DataGrip можно открыть и посмотреь что в ней)
# isolation_level нужно чтобы база даных не проверяла каждое изменение в ней и автоматически их применяло
# check_same_thread нужно чтобы не было ошибки про то что бд используется в другом потоке (хз почему она возникает)
conn = sqlite3.connect('queue.db', isolation_level=None, check_same_thread=False)
cursor = conn.cursor()

# Удаляем прошлую таблицу с пользователями в очереди
cursor.execute('DROP TABLE IF EXISTS queue')

# Создаем новую с полями queuer_id (тип данных: число), queuer (тип данных: строка), time (тип данных: дата)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS queue (
        queuer_id INTEGER PRIMARY KEY,
        queuer TEXT,
        time DATETIME
    )
''')

# Загружаем инфомрацию из файла .env
load_dotenv()

# Создаем класс бота используя токен из .env
bot = telebot.TeleBot(token=getenv("TOKEN"))

# Обработчик команды /start_queue, которая создает новую очередь
@bot.message_handler(commands=['start_queue'])
def start_queue(message: telebot.types.Message) -> None:
    # Удаляем прошлую таблицу с пользователями в очереди
    cursor.execute('DROP TABLE IF EXISTS queue')

    # Создаем новую с полями queuer_id (тип данных: число), queuer (тип данных: строка), time (тип данных: дата)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            queuer_id INTEGER PRIMARY KEY,
            queuer TEXT,
            time DATETIME
        )
    ''')

    # Отправляем сообщение, что создали очередь
    bot.reply_to(message, "Вы создали новую очередь.")

    # reply ничто иное как текст сообщения, котроое отправит бот
    reply = "Люди в очереди:\nПусто."

    # Бот отправляет сообщения привязывая заранее создану клавиатуру keyboard с кнопкой присодениться к сообщению
    bot.reply_to(message, reply, reply_markup=keyboard)
    

# Обработка нажатий на кноаку (изначально уже любых), но в скобочках @bot.callback_query_handler(lambda callback_query: callback_query.data == "join")
# lambda callback_query: callback_query.data == "join" это анонимная функция, которая возвращает True, если была нажата кнопка с действием join и вызывает обработчик
# В ином случае, если нажата кнопка с другим действием, то эта функция не вызывается
@bot.callback_query_handler(lambda callback_query: callback_query.data == "join")
def process_join(callback_query: telebot.types.CallbackQuery) -> None:
    print(f"Получено нажатие кнопки {callback_query.data}")

    # Получаем всех пользователей с таким ID в телеграме, что он равняется ID пользователю нажавшему кнопку
    cursor.execute('SELECT COUNT(*) FROM queue WHERE queuer_id=?', (callback_query.from_user.id,))
    # cursor.fetchone() возвращает массив с одним элементом из бд, но т.к. оно возвращает массив, то все равно нужно получать первый элемент по индексу, то есть по [0]
    count = cursor.fetchone()[0]

    # Если количество равно нулю, то значит, что пользователя нет в очереди и его можно добавить в очередь
    if count == 0:
        # Получаем данные из callback_query в отделньые перменные для удобства и твоего понимания
        queuer_id = callback_query.from_user.id
        queuer = callback_query.from_user.full_name
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Добавляем пользователя в базу данных
        cursor.execute('INSERT INTO queue (queuer_id, queuer, time) VALUES (?, ?, ?)', (queuer_id, queuer, current_time))
        
        # Получаем всех пользователей и сортируем их по времени, так чтобы, те кто нажали первыми были сверху
        cursor.execute('SELECT queuer_id, queuer FROM queue ORDER BY time ASC')

        # Получаем пользователей из запроса выше
        queuers = cursor.fetchall()

        # Создаем переменную, которая будет сообщением бота и добавляем в нее пользователей
        reply = "Люди в очереди:\n"

        # enumerate(list) оно проходится по массиву получая значение и индекс (индекс нам нужен для 1., а значение для Дмитрий Кирилов) (условно)
        # например, for index, value in enumerate(["хуй", "пенис", "вагина"]): print(index, value) будет выводить 
        # 0, хуй
        # 1, пенис
        # 2, вагина
        for index, queuer in enumerate(queuers):
            # Получаем айди и имя, но айди нам не нужно поэтому записываем его как _ (пустая переменная)
            # Если что, это распаковка кортежа (хз, как оно в питоне называется, но в джаваскрипте именно так)
            # Опять же пример, цвет можно хранить в rgb то есть (r, g, b) к примеру белый (255, 255, 255), и чтобы получить r, g, b отдельно в питоне можно написать следующим образом
            # r, g, b = (255, 255, 255)
            # (не ебу как еще обьянить апхахпахп)
            _, name = queuer
            # Добавляем пользователя в строху (увеличиваем индекс на один потому что в массивах идет счет элементов с нуля, а нам нужно показывать с одного)
            reply += f"{index + 1}. {name}\n"

        # Редактируем сообщение с списокм пользователей и добавляем обратно кнопку присоединиться (потому что она каким-то хуем исчезает)
        bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.id, text=reply, reply_markup=keyboard)
        # Показываем красивое всплывающее окно в телеграме с сообщением что вы уже присоеднились, окей да?
        bot.answer_callback_query(callback_query.id, "Вы успешно присоединились к очереди", show_alert=True)
    # Срабатывает если пользователь уже есть в очереди
    else:
        # Показываем красивое всплывающее окно в телеграме с сообщением что вы пользователь уже есть, окей да?
        bot.answer_callback_query(callback_query.id, "Вы уже в очереди", show_alert=True)

# Проверяем проводиться ли запуск с файла main.py, а не из какой нить библиотеки
if __name__ == "__main__":
    # Запускаем бота
    bot.infinity_polling()