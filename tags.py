"""
Работа с тегами аудиофайла. Требуется для изменения статуса.

Используется библиотека [Mutagen](https://mutagen.readthedocs.io).
"""
from io import BytesIO
from mutagen.mp3 import EasyMP3

with open("sample.mp3", "rb") as f: 
    data = f.read() # нужна чтоб нормально применялись теги

buf = BytesIO(data)
buf.seek(0)
audio = EasyMP3(buf) # аудиофайл записанный в память над которым будут производиться все мучения
out = BytesIO() # вывод изменений

def tag_change(title: str = None, artist: str = None):
    """
    Изменение тегов и вывод аудиофайла для загрузки в Telegram.
    """
    out.truncate(0)
    if title:
        audio.tags['title'] = title
    if artist:
        audio.tags['artist'] = artist
    audio.save(out)
    out.seek(0)
    out.name = "Telegram Rich Presence.mp3"
    return out
