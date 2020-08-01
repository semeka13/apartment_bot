import datetime

import telebot
import config
from all_models import User

userStep = {}


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
    print(get_user_step(message.from_user.id))


@bot.message_handler(func=lambda message: get_user_step(message.from_user.id) == 1)
def question_two(message):
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
            except Exception:
                bot.send_message(message.from_user.id, "Время не должно содержать букв")
                return
            tg_id = message.from_user.id
            user = User()
            user.get_from_tg_id(tg_id)
            user.add_transport_time(transport, datetime.time(hour=h, minute=m))
            bot.send_message(message.from_user.id, "Выберете дату своего заезда")
        else:
            bot.send_message(message.from_user.id, "Проверьте,что ввели время в формате чч:мм")
    else:
        bot.send_message(message.from_user.id, "Проверьте,что ввели все данные")



try:
    print("BOT UP", str(datetime.datetime.now()).split(".")[0], sep="\t")
    bot.polling(none_stop=True)
except Exception as e:
    bot.stop_bot()
    print("BOT DOWN", str(datetime.datetime.now()).split(".")[0], sep="\t")
