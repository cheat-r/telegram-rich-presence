"""
Работа с тегами аудиофайла. Требуется для изменения статуса.

Используется библиотека [Mutagen](https://mutagen.readthedocs.io).
"""
from io import BytesIO
from mutagen.mp3 import EasyMP3

class Audio():
    "Класс для работы с аудиотегами."
    def __init__(self):
        with open("sample.mp3", "rb") as f: 
            self.data = f.read() # нужна чтоб нормально применялись теги

        self.buf = BytesIO(self.data)
        self.buf.seek(0)
        self.audio = EasyMP3(self.buf) # аудиофайл записанный в память над которым будут производиться все мучения

    def tag_change(self, title: str = None, artist: str = None):
        """
        Изменение тегов и вывод аудиофайла для загрузки в Telegram.
        """
        out = BytesIO() # вывод изменений
        if title:
            self.audio.tags['title'] = title
        if artist:
            self.audio.tags['artist'] = artist
        self.audio.save(out)
        out.seek(0)
        out.name = "Telegram Rich Presence.mp3"
        return out
