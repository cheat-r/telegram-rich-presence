"""
Работа с Telegram через кастомное приложение. Требует регистрации в [my.telegram.org](https://my.telegram.org).

Используется библиотека [Telethon](https://docs.telethon.dev/).
"""
import logging
from io import BytesIO
from telethon import TelegramClient
#from telethon.tl.functions.users import GetSavedMusicRequest
from telethon.tl.functions.account import SaveMusicRequest


from base64 import b64decode


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

api_id = 0
api_hash = 'nuh-uh, ты должен ввести свои!'

client = TelegramClient('trp', api_id, api_hash)
file = None # Чтобы не засорять чат, будет изменяться один файл и впоследствии удаляться

async def start_client():
    await client.start()

async def stop_client():
    await client.disconnect()

async def update_status(sample: BytesIO, thumb = None):
    """
    Загрузка статуса и его обновление в профиле.
    """
    global file
    _header, b64 = thumb.split(",", 1)
    data = b64decode(b64)
    thumb = BytesIO(data)
    thumb.seek(0)
    if file:
        await client(SaveMusicRequest(file, unsave=True))
        file = await file.edit(file=sample, thumb=thumb)
    else:
        file = await client.send_file('me', sample, thumb=thumb, caption="**Не удаляйте данный файл!**\nОн необходим для работы вашего статуса.")
    result = await client(SaveMusicRequest(file))
    return result

async def delete_status():
    """
    Удаление статуса из профиля.

    Всегда выдаёт True, даже если статуса для удаления нет.
    """
    global file
    result = await client(SaveMusicRequest(file, unsave=True))
    return result

async def delete_cache():
    """
    Удаление файла из избранных.
    
    Вы же не будете его там вечно хранить, так ведь?
    """
    global file
    await file.delete()