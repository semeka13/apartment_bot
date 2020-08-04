import datetime

import telebot
import telebot_calendar
from telebot.types import CallbackQuery, ReplyKeyboardRemove

import config
from all_models import User
import changed



userStep = {}
calendar_1 = telebot_calendar.CallbackData("calendar_1", "action", "year", "month", "day")
telebot_calendar.MONTHS = (
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
    "Декабрь")
telebot_calendar.DAYS = ("ВСК", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ")

def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            try:
                print(str(m.from_user.username) + " [" + str(m.chat.id) + "]: " + m.text)
            except Exception:
                print("[" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(config.TG_TOKEN)
bot.set_update_listener(listener)

def apartment_info(apt):
    return config.apt_desc[apt]

@bot.message_handler(commands=["start"])
def start(message):
    tg_id = message.from_user.id
    user = User()
    status = user.get_from_tg_id(tg_id)["status"]
    if status == "user not found":
        m = "(Сообщение, если произошло первое знакомство)\n\nОписание бота, его функционала"
    else:
        m = "(Сообщение, если пользователь то этого бронировал квартиры)\n\nОписание бота, его функционала"
    bot.send_message(tg_id, m)
    # bot.send_message(tg_id, apartment_info(user.get_apt()["out"]))
    bot.send_message(tg_id, "У меня есть несколько вопросов к тебе.\nЧтобы ответить на них воспользуйся /register")

@bot.message_handler(commands=["register"])
def register(message):
    userStep[message.from_user.id] = 1
    bot.send_message(message.from_user.id,
                     "1. Какой номер вашего рейса и в какое время вы прилетаете в аэропорт Владивостока?\n"
                     "Если на другом транспорте, то на каком и в какое время?\n\n"
                     "Отправьте сообщение в формате:"
                     "\nНомер рейса/транспорт\n"
                     "чч:мм")

@bot.message_handler(func=lambda message: get_user_step(message.from_user.id) == 1)
def question_one(message):
    data = message.text.split("\n")
    if len(data) == 2:
        transport, time = data
        n_time = time.split(":")
        if len(n_time) == 2:
            hours = n_time[0]
            minutes = n_time[1]
            try:
                h = int(hours)
                m = int(minutes)
            except ValueError:
                bot.send_message(message.from_user.id, "Время не должно содержать букв")
                return
            tg_id = message.from_user.id
            user = User()
            user.get_from_tg_id(tg_id)
            user.add_transport_time(transport, datetime.time(hour=h, minute=m))
            bot.send_message(message.from_user.id, "Выберете дату своего заезда")
            now = datetime.datetime.now()  # Get the current date
            bot.send_message(
                message.chat.id,
                "Selected date",
                reply_markup=changed.create_calendar(
                    name=calendar_1.prefix,
                    year=now.year,
                    month=now.month  # Specify the NAME of your calendar
                ),
            )

        else:
            bot.send_message(message.from_user.id, "Проверьте,что ввели время в формате чч:мм")
    else:
        bot.send_message(message.from_user.id, "Проверьте,что ввели все данные")

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Вы выбрали {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1}: Day: {date.strftime('%d.%m.%Y')}")
        bot.send_message(call.from_user.id, "В какое время вы планируете заехать и выехать из номера?\n\n"
                                            "Отправьте сообщение в формате:\n\n"
                                            "чч:мм/чч:мм")
        userStep[call.from_user.id] = 2
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Отмена",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1}: Cancellation")

@bot.message_handler(func=lambda message: userStep[message.from_user.id] == 2)
def question_two(message):
    reply = message.text
    if reply:
        if len(reply.split("/")) == 2:
            time1 = reply.split("/")[0]
            time2 = reply.split("/")[1]
            n_time1 = time1.split(":")
            n_time2 = time2.split(":")
            if len(n_time1) == 2 and len(n_time2) == 2:
                hours1 = n_time1[0]
                minutes1 = n_time1[1]
                hours2 = n_time2[0]
                minutes2 = n_time2[1]
                try:
                    h1 = int(hours1)
                    m1 = int(minutes1)
                    h2 = int(hours2)
                    m2 = int(minutes2)
                except ValueError:
                    bot.send_message(message.from_user.id, "Время не должно содержать букв")
                    print("--- question_two ValueError")
                    return
                tg_id = message.from_user.id
                user = User()
                user.get_from_tg_id(tg_id)
                user.add_start_and_end_time(datetime.time(hour=h1, minute=m1), datetime.time(hour=h2, minute=m2))
                bot.send_message(tg_id,
                                 "Если у вас есть специальные предпочтения во время проживания, то вы можете их написать.")
                userStep[tg_id] = 3
        else:
            bot.send_message(message.from_user.id, "Проверье, что ввели данные в нужном формате")
    else:
        bot.send_message(message.from_user.id, "Проверье, что ввели данные в нужном формате")

@bot.message_handler(func=lambda message: userStep[message.from_user.id] == 3)
def question_three(message):
    if message.text:
        tg_id = message.from_user.id
        user = User()
        user.get_from_tg_id(tg_id)
        user.add_preferences(message.text)
        bot.send_message(tg_id, "Спасибо, мы обязательно всё учтём")
        bot.send_message(tg_id,
                         "Если у вас остались какие-то вопросы, то ва всегда можете их задать, воспользовавшись /question")
    else:
        bot.send_message("Ваше сообщение должно быть текстом")

@bot.message_handler(commands=["question"])
def question(message):
    bot.send_message(message.from_user.id, "Задавайте ваш вопрос")

try:
    print("BOT UP", str(datetime.datetime.now()).split(".")[0], sep="\t")
    bot.polling(none_stop=True)
except Exception as e:
    bot.stop_bot()
    print("BOT DOWN", str(datetime.datetime.now()).split(".")[0], sep="\t")
