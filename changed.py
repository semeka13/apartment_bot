import calendar
import datetime

import telebot_calendar
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot_calendar import CallbackData


MONTHS = (
"Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь")
DAYS = ("ВСК", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ")
CANCEL = "Отмена"

def create_calendar(
    name: str = "calendar", year: int = None, month: int = None,
) -> InlineKeyboardMarkup:
    """
    Create a built in inline keyboard with calendar
    :param name:
    :param year: Year to use in the calendar if you are not using the current year.
    :param month: Month to use in the calendar if you are not using the current month.
    :return: Returns an InlineKeyboardMarkup object with a calendar.
    """

    now_day = datetime.datetime.now()

    if year is None:
        year = now_day.year
    if month is None:
        month = now_day.month

    calendar_callback = CallbackData(name, "action", "year", "month", "day")
    data_ignore = calendar_callback.new("IGNORE", year, month, "!")
    data_months = calendar_callback.new("MONTHS", year, month, "!")

    keyboard = InlineKeyboardMarkup(row_width=7)

    keyboard.add(
        InlineKeyboardButton(
            MONTHS[month - 1] + " " + str(year), callback_data=data_months
        )
    )

    keyboard.add(
        *[InlineKeyboardButton(day, callback_data=data_ignore) for day in DAYS]
    )

    for week in calendar.monthcalendar(year, month):
        row = list()
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            elif (
                f"{now_day.day}.{now_day.month}.{now_day.year}"
                == f"{day}.{month}.{year}"
            ):
                row.append(
                    InlineKeyboardButton(
                        f"({day})",
                        callback_data=calendar_callback.new("DAY", year, month, day),
                    )
                )
            else:
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=calendar_callback.new("DAY", year, month, day),
                    )
                )
        keyboard.add(*row)

    keyboard.add(
        InlineKeyboardButton(
            "<", callback_data=calendar_callback.new("PREVIOUS-MONTH", year, month, "!")
        ),
        InlineKeyboardButton(
            CANCEL, callback_data=calendar_callback.new("CANCEL", year, month, "!")
        ),
        InlineKeyboardButton(
            ">", callback_data=calendar_callback.new("NEXT-MONTH", year, month, "!")
        ),
    )

    return keyboard