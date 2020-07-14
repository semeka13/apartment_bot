import telebot
import config
from all_models import User

TG_TOKEN = config.TG_TOKEN
bot = telebot.TeleBot(TG_TOKEN)
questions_count = 1


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
    bot.send_message(tg_id, apartment_info(user.get_apt()["out"]))
    bot.send_message(tg_id, "У меня есть несколько вопросов к тебе.\nЧтобы ответить на них воспользуйся /register")


@bot.message_handler(commands=["register"])
def register(message):
    bot.send_message(message.from_user.id,
                     "1. Какой номер вашего рейса и в какое время вы прилетаете в аэропорт Владивостока?\n"
                     "Если на другом транспорте, то на каком и в какое время?\n\n"
                     "Отправьте сообщение в формате:"
                     "\nНомер рейса/транспорт\n"
                     "чч:мм")
    questions_count = 2

@bot.callback_query_handler(func=lambda questions_count: 2)
def question_two(message):
    bot.send_message(message.from_user.id, "Выберете дату своего заезда")

bot.polling()