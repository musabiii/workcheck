import time
import threading
from pynput import mouse, keyboard

# Время бездействия в секундах
INACTIVITY_THRESHOLD = 60  # например, 60 секунд

# Флаг активности
last_activity_time = time.time()

# Обработчики событий
def on_activity():
    global last_activity_time
    last_activity_time = time.time()

def on_move(x, y):
    on_activity()

def on_click(x, y, button, pressed):
    if pressed:
        on_activity()

def on_scroll(x, y, dx, dy):
    on_activity()

def on_press(key):
    on_activity()

# Запуск слушателей в фоне
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

print(f"Отслеживание неактивности (порог: {INACTIVITY_THRESHOLD} сек)...")
try:
    while True:
        time.sleep(1)
        if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
            print("❗ Пользователь неактивен более", INACTIVITY_THRESHOLD, "секунд!")
            # Здесь можно добавить своё действие: выключить ПК, отправить уведомление и т.д.
            # Например: os.system("shutdown /s /t 1")  # Windows выключение
            # Или: subprocess.run(["systemctl", "suspend"])  # Linux сон
            # Чтобы не спамить — можно добавить задержку или сброс флага
            time.sleep(INACTIVITY_THRESHOLD)  # ждём ещё раз, чтобы не дублировать
except KeyboardInterrupt:
    print("\nЗавершение...")
finally:
    mouse_listener.stop()
    keyboard_listener.stop()