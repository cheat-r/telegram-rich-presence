"""
Сборник функций для удобства вставки в код.
"""
import platform, os

def pause():
    """
    Приостановка работы программы.

    Предотвращает закрытие программы, что удобно, если нужно дать пользователю **ПОЧИТАТЬ**.
    """
    if platform.system() == "Windows":
        os.system("pause")
    else:
        os.system("/bin/bash -c 'read -s -n 1 -p \"Press any key to continue...\"'")

def clear():
    """
    Очистка консоли.
    
    Потому что много буков — плохо! А больше буков — ещё хуже...
    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")