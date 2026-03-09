"""
Сборник функций для удобства вставки в код.
"""
import platform, os
from io import BytesIO
from aiohttp import ClientSession

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

async def url_to_bytesio(url: str) -> BytesIO:
    """
    Скачивание изображения со ссылки и загрузка его в BytesIO.
    
    Может вернуть плеяду разных ошибок, связанных с соединением, я не следил. :P
    """
    buf = BytesIO()
    async with ClientSession() as sess:
        async with sess.get(url) as resp:
            resp.raise_for_status() # поднимает ошибку в случае если сервер вернёт код ошибки
            async for chunk in resp.content.iter_chunked(64 * 1024):  # куски по 64KB
                buf.write(chunk)
    buf.seek(0)
    return buf
