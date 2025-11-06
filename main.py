import time
import threading
from pynput import mouse, keyboard
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(BOT_TOKEN)

# Время бездействия в секундах
INACTIVITY_THRESHOLD = 10  # например, 60 секунд

# Флаг активности
last_activity_time = time.time()
user_active = True  # Флаг: активен ли пользователь сейчас

# События для синхронизации потоков
activity_event = threading.Event()

# Обработчики событий
def on_activity():
    global last_activity_time, user_active
    last_activity_time = time.time()
    # if user_active == False:
    print("С возвращением!")
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
    reqUrl = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=Пользователь неактивен!"
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
    }
    payload = ""
    response = requests.request("GET", reqUrl, data=payload,  headers=headersList)
    print(response.text)

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print(f"Отслеживание неактивности (порог: {INACTIVITY_THRESHOLD} сек)...")
try:
    while True:
        while user_active:
            time.sleep(1)
            print(time.time())
            if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
                print("❗ Пользователь неактивен более", INACTIVITY_THRESHOLD, "секунд!")
                # Здесь можно добавить своё действие: выключить ПК, отправить уведомление и т.д.
                # Например: os.system("shutdown /s /t 1")  # Windows выключение
                # Или: subprocess.run(["systemctl", "suspend"])  # Linux сон
                # Чтобы не спамить — можно добавить задержку или сброс флага
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