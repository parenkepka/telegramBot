import telebot
bot = telebot.TeleBot('') #импортируем модуль телеграмбот, добавляя свой ТОКЕН

from telebot import types #для добавления интерактивных кнопок

# while True: #эта строка зацикливает бота

@bot.message_handler(content_types=['text']) #объявим метод для получения ТЕКСТОВЫХ сообщений
def start(message): #создание первой функции. Она помогает собрать данные через вопрос
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'В каком городе ты сейчас?')
        bot.register_next_step_handler(message, get_place) #следующий шаг – функция get_place
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start")

def start1(message): #сюда приходит после ошибки и ждет новый введенный текст
    bot.send_message(message.from_user.id, "Попробуйте еще раз. Сокращения тоже пока не распознаю :(\n\nВ каком городе ты сейчас?")
    bot.register_next_step_handler(message, get_place)

def start2(message): #сюда приходит после ссылки на инстаграм и ждет новый введенный текст
    bot.send_message(message.from_user.id, "В каком городе ты сейчас?")
    bot.register_next_step_handler(message, get_place)
    
def get_place(message): #создание второй функции
    global place #глобал говорит о том, что название города можно будет использовать и за пределами этой функции
    place = message.text #здесь бот ждет ввода названия города

    from pyowm import OWM #запуск модуля ПОГОДЫ
    from pyowm.utils import config
    from pyowm.utils import timestamps

    from pyowm.utils.config import get_default_config
    config_dict = get_default_config()
    config_dict['language'] = 'ru' #русификатор модуля

    owm = OWM('368b5c5de702669f657fe1f5b234df16') #персональный ключ для доступа на сервис OWM
    mgr = owm.weather_manager()

    # обработчик исключений на случай, если сервер owm не распознает название города
    try:
        observation = mgr.weather_at_place(place)
        w = observation.weather
        o = w.temperature('celsius').get('temp') #вытаскиваем значение температуры в ЦЕЛЬСИЯХ
        o = round(o) #округляет
        bot.send_message(message.from_user.id, "На улице " + str(o) + " по Цельсию!") #бот отвечает, какая температура


        # блок советов
        if o < -25:
            bot.send_message(message.from_user.id, "Ты что, за полярным кругом?!")
        elif o < -20:
            bot.send_message(message.from_user.id, "ВСЕМ ЛЕЖАТЬ! Лучше под двумя одеялами :)")
        elif o < -10:
            bot.send_message(message.from_user.id, "Ставь чайник и подбери хорошее кино!")
        elif o < -2:
            bot.send_message(message.from_user.id, "Лучше сиди дома!")
        elif o < 0:
            bot.send_message(message.from_user.id, "Идеальная температура, чтобы лепить снеговика, но лучше наблюдать за этим из окна с кружечкой кофе ;)")
        elif o > 0:
            bot.send_message(message.from_user.id, "Не совершай ошибку - не выходи из дома!")
        elif o > 10:
            bot.send_message(message.from_user.id, "Прохладненько...")
        elif o > 20:
            bot.send_message(message.from_user.id, "Чтобы не получить солнечный удар, лучше отсидеться дома!")

        # Этот блок для клавиатуры да/нет
        keyboard = types.InlineKeyboardMarkup() #клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes') #кнопка «Да»
        keyboard.add(key_yes) #добавляем кнопку в клавиатуру
        key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Может, в отпуск?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == "yes":
                bot.send_message(call.message.chat.id, 'Тогда тебе сюда ;)\nhttps://www.instagram.com/blonde_round_the_world/')
            elif call.data == "no":
                bot.send_message(call.message.chat.id, 'Точно? Давай еще раз посмотрим температуру в твоем городе?')
                start2(message) #переспрашиваем через функцию, ОДНАКО ЛУЧШЕ БЫ ЧЕРЕЗ ПЕРЕЗАПУСК БОТА                                           
    
    # обработчик исключений - если ошибка, он возвращает к функции старт1
    except:
        start1(message)

bot.polling(none_stop=True, interval=0)
    # Телеграмм умеет сообщать боту о действиях пользователя двумя способами: через ответ на запрос сервера (Long Poll), 
    # и через Webhook, когда сервер Телеграмма сам присылает сообщение о том, что кто-то написал боту. 
    # Второй способ явно выглядит лучше, но требует выделенного IP-адреса, и установленного SSL на сервере. 
    # В этой статье я хочу рассказать о написании бота, а не настройке сервера, поэтому пользоваться мы будем Long Poll'ом.

# НЕ ЗАБЫТЬ ЗАПУСТИТЬ БОТ в консоли!!! python weather_bot.py
# еще бы повторять код при неполучении ответа с сервера, если ввели неправильное название города