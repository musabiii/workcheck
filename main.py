import sys
import time
import threading
import requests
import os
import logging
from pynput import mouse, keyboard
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(stream=sys.stdout, datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO,
                    format="%(asctime)s %(message)s")



BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

INACTIVITY_THRESHOLD: int = 15 * 60
POMODORO: int = 25 * 60
SHORT_BREAK_GAP: int = 5 * 60

# Тестовые данные
for param in sys.argv:
    if param == '--debug' or param == '-D':
        POMODORO = 10
        SHORT_BREAK_GAP = 5



# Флаг активности
user_active = True  # Флаг: активен ли пользователь сейчас
user_short_break: bool = False

last_activity_time = time.time()
last_inactivity_time: float = float('+inf')

# События для синхронизации потоков
activity_event = threading.Event()

def get_readable_time(ttime):
    ttime_ = time.gmtime(ttime)
    ffmt = f"{"%H ч" if ttime_.tm_hour else ""} {"%M минут" if ttime_.tm_min or (ttime_.tm_min and ttime_.tm_min) else ""} {"%S секунд" if ttime_.tm_sec else ""}"
    return time.strftime(ffmt, ttime_)

# Обработчики событий
def on_activity():
    global last_activity_time, user_active, last_inactivity_time, user_short_break
    if not user_active or user_short_break:
        readable_time = time.strftime('%H:%M:%S', time.localtime(last_activity_time))
        logging.info(f"С возвращением! последняя активность в {readable_time}")
        last_inactivity_time =  time.time()
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
    response = requests.request("GET", req_url, params = params_list, data=payload,  headers=headers_list)
    # logging.info(response.text)

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

logging.info(f"Отслеживание неактивности (порог: {get_readable_time(INACTIVITY_THRESHOLD)})")
try:
    while True:
        last_inactivity_time =  time.time()
        while user_active:
            time.sleep(1)
            # logging.info(time.time())

            if 0 < POMODORO < time.time() - last_inactivity_time and not user_short_break:
                send_notification("Отдохни!")
                last_inactivity_time = float('+inf')

            if time.time() - last_activity_time > SHORT_BREAK_GAP and not user_short_break:
                user_short_break = True
                send_notification("Конец короткого отдыха!", disable_notification=True)
                logging.info("Короткий отдых")


            if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
                logging.info("❗ Слышь, работать! ", INACTIVITY_THRESHOLD, "секунд!")
                user_active = False

                # Получаем текущее время и извлекаем час
                is_work_time = 9 <= time.localtime().tm_hour < 18
                if is_work_time:
                    logging.info("15 минут без активности")
                    send_notification("Слышь, работать! прошло 15 минут")
                else:
                    logging.info("Сейчас нерабочее время")
                # time.sleep(INACTIVITY_THRESHOLD)  # ждём ещё раз, чтобы не дублировать

        activity_event.clear()
        activity_event.wait()
       

except KeyboardInterrupt:
    print("\nЗавершение...")
finally:
    mouse_listener.stop()
    keyboard_listener.stop()