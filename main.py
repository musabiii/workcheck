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

# Флаг активности
last_activity_time = time.time()
user_active = True  # Флаг: активен ли пользователь сейчас

# События для синхронизации потоков
activity_event = threading.Event()

# Обработчики событий
def on_activity():
    global last_activity_time, user_active, last_inactivity_time
    if not user_active:
        readable_time = time.strftime('%H:%M:%S', time.localtime(last_activity_time))
        print(f"С возвращением! последняя активность в {readable_time}")
        last_inactivity_time =  time.time();
    last_activity_time = time.time()
    user_active = True
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

def send_notification():
    print(BOT_TOKEN)
    msg = "Слышь, работать! прошло 15 минут"
    req_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    headers_list = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
    }
    payload = ""
    response = requests.request("GET", req_url, data=payload,  headers=headers_list)
    print(response.text)

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print(f"Отслеживание неактивности (порог: {INACTIVITY_THRESHOLD} сек)...")
try:
    while True:
        last_inactivity_time =  time.time()
        while user_active:
            time.sleep(1)
            # print(time.time())
            if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
                print("❗ Слышь, работать! ", INACTIVITY_THRESHOLD, "секунд!")
                user_active = False
                send_notification()
                # time.sleep(INACTIVITY_THRESHOLD)  # ждём ещё раз, чтобы не дублировать

        activity_event.clear()
        activity_event.wait()
       

except KeyboardInterrupt:
    print("\nЗавершение...")
finally:
    mouse_listener.stop()
    keyboard_listener.stop()