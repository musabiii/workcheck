import time
import threading
from pynput import mouse, keyboard
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Время бездействия в секундах
INACTIVITY_THRESHOLD = 15 * 60
POMODORO = 25 * 60
SHORT_BREAK_GAP = 5 * 60

# Тестовые данные
# POMODORO = 10
# SHORT_BREAK_GAP = 5

user_short_break: bool = False

# Флаг активности
last_activity_time = time.time()
last_inactivity_time: float = float('+inf')

user_active = True  # Флаг: активен ли пользователь сейчас

# События для синхронизации потоков
activity_event = threading.Event()

def get_readable_time(ttime, format = "%H:%M:%S"):
    return time.strftime(format, time.localtime(ttime))

# Обработчики событий
def on_activity():
    global last_activity_time, user_active, last_inactivity_time, user_short_break
    if not user_active or user_short_break:
        # readable_time = time.strftime('%H:%M:%S', time.localtime(last_activity_time))
        print(f"С возвращением! последняя активность в {get_readable_time(last_activity_time)}")
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
    print(response.text)

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print(f"Отслеживание неактивности (порог: {get_readable_time(INACTIVITY_THRESHOLD, "%H:%M:%S")} сек)...")
try:
    while True:
        last_inactivity_time =  time.time()
        while user_active:
            time.sleep(1)
            # print(time.time())

            if 0 < POMODORO < time.time() - last_inactivity_time and not user_short_break:
                send_notification("Отдохни!")
                last_inactivity_time = float('+inf')

            if time.time() - last_activity_time > SHORT_BREAK_GAP and not user_short_break:
                user_short_break = True
                send_notification("Конец короткого отдыха!", disable_notification=True)
                print("short break")


            if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
                print("❗ Слышь, работать! ", INACTIVITY_THRESHOLD, "секунд!")
                user_active = False

                # Получаем текущее время и извлекаем час
                is_work_time = 9 <= time.localtime().tm_hour < 18
                if is_work_time:
                    print("Сейчас рабочее время (с 9:00 до 18:00)")
                    send_notification("Слышь, работать! прошло 15 минут")
                else:
                    print("Сейчас нерабочее время")
                # time.sleep(INACTIVITY_THRESHOLD)  # ждём ещё раз, чтобы не дублировать

        activity_event.clear()
        activity_event.wait()
       

except KeyboardInterrupt:
    print("\nЗавершение...")
finally:
    mouse_listener.stop()
    keyboard_listener.stop()