import datetime as dt
import os
import re
from typing import Dict, List, Optional, Tuple
import threading

import telebot
from telebot import types


# ===================== НАСТРОЙКИ =====================
TOKEN = os.getenv("BOT_TOKEN")  # строка-токен из env
if not TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в переменных окружения")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

SEMESTER_START = dt.date(2026, 2, 9)
WEEK1_IS_ODD = True
# =====================================================

DAY_ORDER = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
DAY_MAP = {
    "ПН": "Понедельник",
    "ВТ": "Вторник",
    "СР": "Среда",
    "ЧТ": "Четверг",
    "ПТ": "Пятница",
    "СБ": "Суббота",
    "ВС": "Воскресенье",
}

# ===================== РАСПИСАНИЕ ИТД-223 =====================
SCHEDULE: Dict[str, Dict[str, List[dict]]] = {
    "odd": {
        "ПН": [
            {"pair_no": 4, "time": "14:25-15:45", "aud": None, "teacher": None, "kind": None, "subject": "Майнор"},
            {"pair_no": 5, "time": "16:05-17:25", "aud": None, "teacher": None, "kind": None, "subject": "Майнор"},
            {"pair_no": 6, "time": "17:40-19:00", "aud": None, "teacher": None, "kind": None, "subject": "Майнор"},
        ],
        "ВТ": [],
        "СР": [
            {"pair_no": 1, "time": "09:15-10:35", "aud": "спорт. зал", "teacher": "Харламов В.И.  / Якутина Н.В.", "kind": "пр",
             "subject": "Элективные дисциплины по физической культуре и спорту"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "3203", "teacher": "Груздева М.А.", "kind": "Лаб",
             "subject": "Проектирование информационных систем в дизайне"},
            {"pair_no": 3, "time": "12:25-13:45", "aud": "3320", "teacher": "Косолапов Р.К.", "kind": "Пр",
             "subject": "Управление данными"},
            {"pair_no": 4, "time": "14:25-15:45", "aud": "3320", "teacher": "Косолапов Р.К.", "kind": "Лаб",
             "subject": "Управление данными"},
        ],
        "ЧТ": [
            {"pair_no": 1, "time": "09:15-10:35", "aud": "дист", "teacher": "Борзунов Г.И.", "kind": "Лек",
             "subject": "Компьютерная обработка изображений"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "дист", "teacher": "Каршакова Л.Б.", "kind": "Лек",
             "subject": "Основы дизайн-проекта"},
        ],
        "ПТ": [],
        "СБ": [],
        "ВС": [],
    },
    "even": {
        "ПН": [
            {"pair_no": 1, "time": "09:55-10:35", "aud": "дист", "teacher": "Иванов В.В.", "kind": "Лек",
             "subject": "Методы и средства проектирования информационных систем и технологий"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "дист", "teacher": "Иванов В.В.", "kind": "Лек",
             "subject": "Методы и средства проектирования информационных систем и технологий"},
            {"pair_no": 3, "time": "12:25-13:45", "aud": "дист", "teacher": "Косолапов Р.К.", "kind": "Лек",
             "subject": "Управление данными"},
            {"pair_no": 4, "time": "14:25-15:45", "aud": "дист", "teacher": "Груздева М.А.", "kind": "Лек",
             "subject": "Проектирование информационных систем в дизайне"},
        ],
        "ВТ": [],
        "СР": [
            {"pair_no": 1, "time": "09:55-10:35", "aud": "3203", "teacher": "Груздева М.А.", "kind": "Лаб",
             "subject": "Проектирование информационных систем в дизайне"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "3203", "teacher": "Груздева М.А.", "kind": "Лаб",
             "subject": "Проектирование информационных систем в дизайне"},
            {"pair_no": 3, "time": "12:25-13:45", "aud": "3320", "teacher": "Косолапов Р.К.", "kind": "Пр",
             "subject": "Управление данными"},
            {"pair_no": 4, "time": "14:25-15:45", "aud": "3320", "teacher": "Косолапов Р.K.", "kind": "Лаб",
             "subject": "Управление данными"},
        ],
        "ЧТ": [
            {"pair_no": 1, "time": "09:15-10:35", "aud": "дист", "teacher": "Борзунов Г.И.", "kind": "Лек",
             "subject": "Компьютерная обработка изображений"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "дист", "teacher": "Каршакова Л.Б.", "kind": "Лек",
             "subject": "Основы дизайн-проекта"},
            {"pair_no": 4, "time": "14:25-15:45", "aud": "3202", "teacher": "Новикова П.А.", "kind": "Лаб",
             "subject": "Компьютерная обработка изображений"},
            {"pair_no": 5, "time": "16:05-17:25", "aud": "3202", "teacher": "Новикова П.А.", "kind": "Лаб",
             "subject": "Компьютерная обработка изображений"},
            {"pair_no": 6, "time": "17:40-19:00", "aud": "3202", "teacher": "Новикова П.А.", "kind": "Пр",
             "subject": "Компьютерная обработка изображений"},
        ],
        "ПТ": [
            {"pair_no": 2, "time": "10:50-12:10", "aud": "спорт. зал", "teacher": "Харламов В.И.  / Якутина Н.В.", "kind": "пр",
             "subject": "Элективные дисциплины по физической культуре и спорту"},
            {"pair_no": 3, "time": "12:25-13:45", "aud": "3304", "teacher": "Каршакова Л.Б.", "kind": "Лаб",
             "subject": "Основы дизайн-проекта"},
            {"pair_no": 4, "time": "14:25-15:45", "aud": "3304", "teacher": "Каршакова Л.Б.", "kind": "Лаб",
             "subject": "Основы дизайн-проекта"},
        ],
        "СБ": [
            {"pair_no": 1, "time": "09:55-10:35", "aud": "3302", "teacher": "Грибова Е.В.", "kind": "Лаб",
             "subject": "Методы и средства проектирования информационных систем и технологий"},
            {"pair_no": 2, "time": "10:50-12:10", "aud": "3302", "teacher": "Грибова Е.В.", "kind": "Лаб",
             "subject": "Методы и средства проектирования информационных систем и технологий"},
            {"pair_no": 3, "time": "12:25-13:45", "aud": "3302", "teacher": "Грибова Е.В.", "kind": "Пр",
             "subject": "Методы и средства проектирования информационных систем и технологий"},
        ],
        "ВС": [],
    },
}
# =====================================================

SUBJECT_EMOJI = {
    "Майнор": "🎯",
    "Элективные дисциплины по физической культуре и спорту": "🏃‍♀️",
    "Проектирование информационных систем в дизайне": "🧩",
    "Управление данными": "🗄️",
    "Компьютерная обработка изображений": "🖼️",
    "Основы дизайн-проекта": "🎨",
    "Методы и средства проектирования информационных систем и технологий": "🏗️",
}

def subject_emoji(subject: str) -> str:
    return SUBJECT_EMOJI.get(subject, "📌")

def is_distance_lecture(lesson: dict) -> bool:
    aud = str(lesson.get("aud") or "").strip().lower()
    kind = str(lesson.get("kind") or "").strip().lower()
    return aud == "дист" and ("лек" in kind)

def parse_time_range(time_range: Optional[str]) -> Optional[Tuple[dt.time, dt.time]]:
    if not time_range:
        return None
    m = re.match(r"^\s*(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\s*$", time_range)
    if not m:
        return None
    start = dt.time(int(m.group(1)), int(m.group(2)))
    end = dt.time(int(m.group(3)), int(m.group(4)))
    return start, end

def start_minutes(L: dict) -> int:
    tr = parse_time_range(L.get("time"))
    if not tr:
        return 10**9
    return tr[0].hour * 60 + tr[0].minute

def dt_from_time(date_: dt.date, t: dt.time) -> dt.datetime:
    return dt.datetime.combine(date_, t)

def minutes_between(a: dt.datetime, b: dt.datetime) -> int:
    return int((b - a).total_seconds() // 60)

def format_break_minutes(mins: int) -> str:
    if mins < 0:
        mins = 0
    return f"🕒 Перерыв: *{mins} мин*"

def format_lesson_block(L: dict) -> str:
    subj = str(L.get("subject") or "").strip()
    emo = subject_emoji(subj)

    lines = [
        f"*{L['pair_no']} пара ({L['time']})*",
        f"{emo} *{subj}*",
    ]

    if is_distance_lecture(L):
        lines.append("💻 Лекция дистанционно")
    else:
        aud = L.get("aud")
        if aud:
            lines.append(f"🏫 Ауд: {aud}")

    teacher = L.get("teacher")
    if teacher:
        lines.append(f"👤 {teacher}")

    return "\n".join(lines)

def week_parity(date_: dt.date) -> str:
    delta_weeks = (date_ - SEMESTER_START).days // 7
    is_odd = (delta_weeks % 2 == 0) if WEEK1_IS_ODD else (delta_weeks % 2 == 1)
    return "odd" if is_odd else "even"

def day_abbr_from_date(date_: dt.date) -> str:
    return DAY_ORDER[date_.weekday()]

def monday_of_week(date_: dt.date) -> dt.date:
    return date_ - dt.timedelta(days=date_.weekday())

def date_for_day_in_week(week_monday: dt.date, day_abbr: str) -> dt.date:
    return week_monday + dt.timedelta(days=DAY_ORDER.index(day_abbr))

def choose_week_monday(today: dt.date, next_week: bool) -> dt.date:
    base = monday_of_week(today)
    return base + dt.timedelta(days=7) if next_week else base

def get_lessons_for_date(date_: dt.date) -> List[dict]:
    parity = week_parity(date_)
    day_abbr = day_abbr_from_date(date_)
    lessons = SCHEDULE[parity].get(day_abbr, [])
    return sorted(lessons, key=lambda x: (x["pair_no"], start_minutes(x)))

def format_day(date_: dt.date, label: Optional[str] = None) -> str:
    parity = week_parity(date_)
    day_abbr = day_abbr_from_date(date_)
    nice_day = DAY_MAP[day_abbr]
    parity_ru = "Нечетная" if parity == "odd" else "Четная"

    lessons = get_lessons_for_date(date_)

    head_label = f" — {label}" if label else ""
    header = (
        f"📅 {nice_day} ({day_abbr}){head_label}\n"
        f"🔁 Неделя: *{parity_ru}*\n"
        f"🗓 Дата: {date_.strftime('%d.%m.%Y')}\n"
    )

    if not lessons:
        return header + "\nВыходной 🎊"

    blocks = [header]
    for i, L in enumerate(lessons):
        blocks.append("\n" + format_lesson_block(L))
        if i < len(lessons) - 1:
            cur_tr = parse_time_range(L.get("time"))
            nxt_tr = parse_time_range(lessons[i + 1].get("time"))
            if cur_tr and nxt_tr:
                end_dt = dt_from_time(date_, cur_tr[1])
                next_start_dt = dt_from_time(date_, nxt_tr[0])
                gap = minutes_between(end_dt, next_start_dt)
                blocks.append("\n" + format_break_minutes(gap))
    return "\n".join(blocks)

def current_lesson(now: dt.datetime) -> Optional[Tuple[dict, dt.datetime, int]]:
    lessons = get_lessons_for_date(now.date())
    for L in lessons:
        tr = parse_time_range(L.get("time"))
        if not tr:
            continue
        start_t, end_t = tr
        start_dt = dt_from_time(now.date(), start_t)
        end_dt = dt_from_time(now.date(), end_t)
        if start_dt <= now < end_dt:
            minutes_left = int((end_dt - now).total_seconds() // 60)
            return L, end_dt, minutes_left
    return None

def next_lesson(now: dt.datetime) -> Optional[Tuple[dict, dt.datetime, int]]:
    lessons = get_lessons_for_date(now.date())
    for L in lessons:
        tr = parse_time_range(L.get("time"))
        if not tr:
            continue
        start_t, _ = tr
        start_dt = dt_from_time(now.date(), start_t)
        if start_dt > now:
            minutes_to = int((start_dt - now).total_seconds() // 60)
            return L, start_dt, minutes_to
    return None

def format_current_pair_message(L: dict, minutes_left: int) -> str:
    return format_lesson_block(L) + f"\n\n⏳ До конца: *{minutes_left} мин*"

def format_next_pair_message(L: dict, minutes_to: int) -> str:
    return "➡️ Следующая пара:\n\n" + format_lesson_block(L) + f"\n\n⏱ До начала: *{minutes_to} мин*"


HELP_TEXT = (
    "Я бот расписания *ИТД-223*.\n\n"
    "Что ты можешь посмотреть:\n"
    "• Пары сегодня 📚\n"
    "• Текущая пара 🕖\n"
    "• Следующая пара ➡️\n"
    "• Пары завтра 📚\n"
    "• Расписание этой недели 📅\n"
    "• Расписание следующей недели 📅\n\n"
)

DAY_KB_BACK = "⬅️ Назад"
WEEK_MODE_THIS = "THIS"
WEEK_MODE_NEXT = "NEXT"
user_week_mode: Dict[int, str] = {}

# ---- клавиатуры ----
def main_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("Пары сегодня 📚"), types.KeyboardButton("Текущая пара 🕖"))
    kb.row(types.KeyboardButton("Следующая пара ➡️"), types.KeyboardButton("Пары завтра 📚"))
    kb.row(types.KeyboardButton("Эта неделя 📅"), types.KeyboardButton("След. неделя 📅"))
    return kb

def week_days_menu_for_week_monday(week_monday: dt.date) -> types.ReplyKeyboardMarkup:
    parity = week_parity(week_monday)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    row = []
    for d in DAY_ORDER:
        if SCHEDULE[parity].get(d):
            row.append(types.KeyboardButton(d))
            if len(row) == 4:
                kb.row(*row)
                row = []
    if row:
        kb.row(*row)

    if kb.keyboard == []:
        kb.row(types.KeyboardButton("На этой неделе нет пар 🎊"))

    kb.row(types.KeyboardButton(DAY_KB_BACK))
    return kb


# ---- таймер обновления текущей пары ----
active_timer: Dict[int, threading.Event] = {}  # chat_id -> stop_event

def run_current_timer(chat_id: int, message_id: int):
    stop_event = active_timer.get(chat_id)
    if not stop_event:
        return

    while not stop_event.is_set():
        now = dt.datetime.now()
        cur = current_lesson(now)
        if not cur:
            try:
                bot.edit_message_text(
                    "Сейчас пара не идёт 🙂",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=main_keyboard()
                )
            except Exception:
                pass
            break

        L, end_dt, minutes_left = cur
        try:
            bot.edit_message_text(
                format_current_pair_message(L, minutes_left),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=main_keyboard(),
                parse_mode="Markdown",
            )
        except Exception:
            # если сообщение нельзя редактировать/уже удалено и т.п.
            pass

        sec_left = (end_dt - now).total_seconds()
        sleep_for = min(60, max(5, int(sec_left)))
        stop_event.wait(timeout=sleep_for)

    active_timer.pop(chat_id, None)


# ===================== ХЭНДЛЕРЫ =====================
@bot.message_handler(commands=["start"])
def start(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот расписания *ИТД-223*.\n"
        "Нажми /help — помощь.\n\n"
        "Выбирай кнопку 👇",
        reply_markup=main_keyboard(),
    )

@bot.message_handler(commands=["help"])
def help_cmd(message: types.Message):
    bot.send_message(message.chat.id, HELP_TEXT, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: (m.text or "").lower() in ["help", "помощь"])
def help_text_alias(message: types.Message):
    bot.send_message(message.chat.id, HELP_TEXT, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "Пары сегодня 📚")
def today(message: types.Message):
    bot.send_message(
        message.chat.id,
        format_day(dt.date.today(), "Сегодня"),
        reply_markup=main_keyboard(),
    )

@bot.message_handler(func=lambda m: m.text == "Пары завтра 📚")
def tomorrow(message: types.Message):
    d = dt.date.today() + dt.timedelta(days=1)
    bot.send_message(
        message.chat.id,
        format_day(d, "Завтра"),
        reply_markup=main_keyboard(),
    )

@bot.message_handler(func=lambda m: m.text == "Следующая пара ➡️")
def nxt(message: types.Message):
    now = dt.datetime.now()

    cur = current_lesson(now)
    if cur:
        L, _, minutes_left = cur
        bot.send_message(
            message.chat.id,
            "Сейчас уже идёт пара:\n\n" + format_current_pair_message(L, minutes_left),
            reply_markup=main_keyboard(),
        )
        return

    n = next_lesson(now)
    if not n:
        bot.send_message(message.chat.id, "Сегодня больше пар нет 🥳", reply_markup=main_keyboard())
        return

    L, _, minutes_to = n
    bot.send_message(
        message.chat.id,
        format_next_pair_message(L, minutes_to),
        reply_markup=main_keyboard(),
    )

@bot.message_handler(func=lambda m: m.text == "Текущая пара 🕖")
def current(message: types.Message):
    now = dt.datetime.now()
    cur = current_lesson(now)
    if not cur:
        bot.send_message(message.chat.id, "Сейчас пара не идёт 🙂", reply_markup=main_keyboard())
        return

    # если таймер уже запущен — не плодим потоки
    if message.chat.id in active_timer and not active_timer[message.chat.id].is_set():
        bot.send_message(
            message.chat.id,
            "🕖 Таймер уже запущен (обновляет последнее сообщение).",
            reply_markup=main_keyboard(),
        )
        return

    L, _, minutes_left = cur
    sent = bot.send_message(
        message.chat.id,
        format_current_pair_message(L, minutes_left),
        reply_markup=main_keyboard(),
    )

    stop_event = threading.Event()
    active_timer[message.chat.id] = stop_event
    t = threading.Thread(target=run_current_timer, args=(message.chat.id, sent.message_id), daemon=True)
    t.start()

@bot.message_handler(func=lambda m: m.text == "Эта неделя 📅")
def week_this(message: types.Message):
    user_week_mode[message.chat.id] = WEEK_MODE_THIS
    week_monday = choose_week_monday(dt.date.today(), next_week=False)
    bot.send_message(
        message.chat.id,
        "Выбери день 👇",
        reply_markup=week_days_menu_for_week_monday(week_monday),
    )

@bot.message_handler(func=lambda m: m.text == "След. неделя 📅")
def week_next(message: types.Message):
    user_week_mode[message.chat.id] = WEEK_MODE_NEXT
    week_monday = choose_week_monday(dt.date.today(), next_week=True)
    bot.send_message(
        message.chat.id,
        "Выбери день 👇",
        reply_markup=week_days_menu_for_week_monday(week_monday),
    )

@bot.message_handler(func=lambda m: (m.text or "").strip() in DAY_ORDER)
def week_day(message: types.Message):
    mode = user_week_mode.get(message.chat.id, WEEK_MODE_THIS)
    next_week = (mode == WEEK_MODE_NEXT)
    week_monday = choose_week_monday(dt.date.today(), next_week=next_week)
    d = date_for_day_in_week(week_monday, message.text.strip())
    bot.send_message(message.chat.id, format_day(d), reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "На этой неделе нет пар 🎊")
def no_week(message: types.Message):
    bot.send_message(message.chat.id, "На этой неделе пар нет 🎊", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == DAY_KB_BACK)
def back(message: types.Message):
    bot.send_message(message.chat.id, "Ок 👇", reply_markup=main_keyboard())


if __name__ == "__main__":
    # long_polling
    bot.infinity_polling(timeout=30, long_polling_timeout=30)