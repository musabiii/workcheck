import sys
import time
import threading
import requests
import os
import logging
from pynput import mouse, keyboard
from dotenv import load_dotenv
import pendulum
import random
from plyer import notification

load_dotenv()
logging.basicConfig(stream=sys.stdout, datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    format="%(asctime)s %(message)s")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

INACTIVITY_THRESHOLD: int = 15 * 60
POMODORO: int = 25 * 60
POMODORO_2: int = 40 * 60
SHORT_BREAK_GAP: int = 5 * 60
INACTIVITY_SHORT: int = 5 * 60

# Тестовые данные
# for param in sys.argv:
for i, param in enumerate(sys.argv):
    if param == '--debug' or param == '-D':
        POMODORO = 10
        SHORT_BREAK_GAP = 5
        INACTIVITY_THRESHOLD: int = 15
    if param == '--long' or param == '-L':
        POMODORO = 40*60
        INACTIVITY_THRESHOLD = 25*60
        SHORT_BREAK_GAP = 10*60
    if param == '--pomodoro' or param == '-P':
        POMODORO = 10
        if i + 1 < len(sys.argv):
            POMODORO = int(sys.argv[i + 1]) * 60
            logging.info(f"POMODORO: {POMODORO}")

# Флаг активности
user_active = True  # Флаг: активен ли пользователь сейчас
user_short_break = pomodoro_notified = pomodoro_2_notified = False

last_activity_time = time.time()
last_inactivity_time: float = float('+inf')
worked_time = 0
away_time = 0

# События для синхронизации потоков
activity_event = threading.Event()

if __name__ == '__main__':
    print("this is mine")

def main():
    print("this is mine")

def notify_log(title, msg = "_"):
   logging.info(title + " " + msg if msg else "")
   try:
       notify_win(title, msg)
   except Exception as e:
       logging.error(e)
    

def notify_win(title: str, msg = '_') -> None:
    notification.notify(title=title, message=msg, app_name='Work check', timeout=20)

def get_readable_seconds(sec):
    delta = pendulum.from_timestamp(sec) - pendulum.from_timestamp(0)
    return delta.in_words(locale='ru')

def get_readable_interval(start, end):
    delta = pendulum.from_timestamp(end) - pendulum.from_timestamp(start)
    return delta.in_words(locale='ru')

# Обработчики событий
def on_activity():
    global last_activity_time, user_active, last_inactivity_time, user_short_break, pomodoro_notified, pomodoro_2_notified, away_time
    if not user_active or user_short_break:
        readable_interval = get_readable_interval(last_activity_time, time.time())
        away_time = away_time + (time.time() - last_activity_time)
        notify_log(f"С возвращением! Вас не было {readable_interval}!", f"всего вне работы {get_readable_seconds(away_time)}"
                                                                        f"\n{random_quote()}")
        last_inactivity_time =  time.time()
        pomodoro_notified = pomodoro_2_notified = False
    last_activity_time = time.time()
    user_active = True
    user_short_break = False
    activity_event.set()  # Пробуждаем главный поток, если ждём активности

def on_move(x, y):
    on_activity()

def on_click(x, y, button, pressed):
    if pressed:
        on_activity()

def on_scroll(x, y, dx, dy):
    on_activity()

def on_press(key):
    on_activity()

def send_notification(msg, disable_notification = False):
    req_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    headers_list = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
    }
    params_list = {
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_notification": disable_notification,
    }
    payload = ""
    try:
        response = requests.request("GET", req_url, params = params_list, data=payload,  headers=headers_list)
    except:
        logging.error("не удалось отправить тг")

def whitegap(n):
    result = ""
    for i in range(n):
        result += " "
    return result

def random_quote():
    quotes = [
        "Сделай сегодня то, что другие не хотят — завтра будешь жить так, как другие не могут.",
        "Маленькие шаги каждый день дают большие результаты.",
        "Дисциплина — это выбор в пользу будущего.",
        "Лучшее время начать — сейчас.",
        "Фокус сильнее мотивации.",
        "Не нужно быть лучшим — нужно быть лучше, чем вчера.",
        "Сомнение убивает больше мечт, чем неудача.",
        "Большие задачи решаются маленькими действиями.",
        "Работай тихо — пусть успех создаёт шум.",
        "Если не контролируешь день — день контролирует тебя.",
        "Привычки важнее силы воли.",
        "Делай трудное первым.",
        "Прогресс важнее идеала.",
        "Не скорость, а постоянство ведёт к результату.",
        "Одна задача за раз — и гора становится холмом.",
        "Сегодняшний труд — завтрашняя свобода.",
        "Сосредоточься на процессе, а не на шуме вокруг.",
        "Результат — это сумма ежедневных усилий.",
        "Каждый повтор укрепляет характер.",
        "Отвлечения — враг роста.",
        "План без действия — просто мечта.",
        "Лучше сделать хотя бы 1% сегодня, чем ждать идеального момента.",
        "Успех — это когда дисциплина встречает время.",
        "Твоя продуктивность — твоя суперсила.",
        "Небольшой прогресс всё равно прогресс.",
        "Когда фокус есть — результат неизбежен.",
        "Работай умно, а не много.",
        "Сделай себя человеком, который делает.",
        "Стань тем, кто заканчивает начатое.",
        "Если задача занимает 5 минут — сделай её сразу.",
        "Сложное — не значит невозможное.",
        "Сначала дисциплина, потом вдохновение.",
        "Ты ближе к цели, чем кажется.",
        "Перфекционизм — форма прокрастинации.",
        "Не думай о всём — думай о следующем шаге.",
        "Твой будущий ты благодарит тебя за сегодняшний выбор.",
        "Контроль над временем — контроль над жизнью.",
        "Просто начни — остальное подтянется.",
        "Делай. Отдыхай. Делай снова.",
        "Терпение + действие = результат.",
        "Один сфокусированный час ценнее десяти рассеянных.",
        "Учись отдыхать, а не сдаваться.",
        "Настоящий рост начинается в неудобстве.",
        "Тебе не нужно быть идеальным — тебе нужно быть последовательным.",
        "Ставь цель — и двигайся к ней каждый день.",
        "Маленькие победы ведут к большим.",
        "Если хочешь изменить жизнь — начни с дня.",
        "Ты делаешь больше, чем тебе кажется.",
        "Каждое усилие имеет значение.",
        "Твой потенциал раскрывается в действии."
    ]
    return random.choice(quotes)

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

logging.info(f"Отслеживание неактивности "
            f"(порог: {get_readable_seconds(INACTIVITY_THRESHOLD)})"
            f" Перерыв {get_readable_seconds(SHORT_BREAK_GAP)}"
            f" \n{whitegap(20)}POMODORO {get_readable_seconds(POMODORO)} POMODORO_2 {get_readable_seconds(POMODORO_2)}"
            f"\n\n{whitegap(20)}{random_quote()}")

try:
    while True:
        last_inactivity_time =  time.time()
        while user_active:
            time.sleep(1)
            # logging.info(time.time())

            if (0 < POMODORO < (time.time() - last_inactivity_time)) and not pomodoro_notified:
                send_notification("Отдохни!")
                notify_log("Пора отдохнуть")
                pomodoro_notified = True
            if (0 < POMODORO_2 < (time.time() - last_inactivity_time)) and not pomodoro_2_notified:
                send_notification("Отдохни!")
                notify_log("Пора отдохнуть")
                pomodoro_2_notified = True

            # if time.time() - last_activity_time > INACTIVITY_SHORT and not user_short_break:
            #     # d
            #
            if time.time() - last_activity_time > SHORT_BREAK_GAP and not user_short_break:
                user_short_break = pomodoro_notified = True
                send_notification("Конец короткого отдыха!", disable_notification=True)
                worked_time = worked_time + (last_activity_time - last_inactivity_time)
                notify_log(f"Короткий отдых, поработали {get_readable_interval(last_inactivity_time, last_activity_time)}!", f"всего отработано {get_readable_seconds(worked_time)}")

            if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
                user_active = False

                is_work_time = (9 <= time.localtime().tm_hour < 18)
                if is_work_time:
                    logging.info("15 минут без активности")
                    send_notification(f"❗ Слышь, работать! Прошло {get_readable_seconds(INACTIVITY_THRESHOLD)}")
                else:
                    logging.info("15 минут без активности, сейчас нерабочее время")

        activity_event.clear()
        activity_event.wait()
       

except KeyboardInterrupt:
    print("\nЗавершение...")
finally:
    mouse_listener.stop()
    keyboard_listener.stop()