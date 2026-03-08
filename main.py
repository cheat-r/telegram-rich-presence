"""
Основной файл. Импортирует все модули и запускает веб-сервер.
"""
import asyncio
from io import BytesIO
from aiohttp import web, ClientSession, ClientResponseError, ClientConnectorError
from socket import gaierror
from client import Client
from tags import Audio
from config import config

from base64 import b64decode
from colorama import init, Fore, Back, Style

cache_title = cache_artist = None # так как premid отдаёт запрос на каждое действие (пауза и воспроизведение), то лучше не дёргать лишний раз телегу, нам же проще будет
cache_image = {} # лишние запросы в сеть стараемся не делать, здесь будут сохраняться мини-превьюхи (они и так занимают мало места)
app = web.Application()
routes = web.RouteTableDef()
client = Client()
audio = Audio()
init(autoreset=True)

async def url_to_bytesio(url: str, session_http: ClientSession) -> BytesIO:
    """
    Скачивание изображения со ссылки и загрузка его в BytesIO.
    
    Может вернуть плеяду разных ошибок, связанных с соединением, я не следил. :P
    """
    buf = BytesIO()
    async with session_http.get(url) as resp:
        resp.raise_for_status() # поднимает ошибку в случае если сервер вернёт код ошибки
        async for chunk in resp.content.iter_chunked(64 * 1024):  # куски по 64KB
            buf.write(chunk)
    buf.seek(0)
    return buf

@routes.get('/')
async def sillyyou(request: web.Request):
    return web.Response(text='Если вы видите этот текст, TRP определённо работает!\nЗдесь вам нечего делать, ибо веб-сервер хостится не для вас, но для PreMiD (и возможных будущих расширений?).')

@routes.get('/trp/premid')
async def areyoukidding(request: web.Request):
    return web.Response(text='Ваша любопытность крайне ценится, однако здесь вам нечего делать.')

@routes.post('/trp/premid')
async def premid(request: web.Request):
    """
    Последовательность действий при получении запроса от PreMiD.
    """
    global cache_artist, cache_title
    data = await request.json()
    active_activity = data['active_activity']

    if not active_activity:
        await client.delete_status() # удаляем статус, так как отсутствует активная активность
        return web.Response()
    if not 'details' in active_activity:
        print(Fore.LIGHTYELLOW_EX + 'Кажется, мы потеряли соединение с интернетом... Либо активность решила выпендриться и выкинуть пустые данные. Зараза.')
        await client.delete_status()
        return web.Response()
    title = f"{active_activity['details']}"
    if not 'state' in active_activity: # оказывается так тоже может быть???
        artist = f"{active_activity['service']}"
    else:
        artist = f"{active_activity['service']} | {active_activity['state']}"
    image = active_activity['assets']['large_image']
    #print(Back.LIGHTBLACK_EX + Fore.LIGHTBLUE_EX + title)
    #print(Back.LIGHTBLACK_EX + Fore.LIGHTBLUE_EX + artist)
    #print(Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX + image)
    
    if title == cache_title and artist == cache_artist:
        print(Fore.MAGENTA + 'Совпадение с предыдущим запросом!')
        return web.Response() # не делаем повторное обновление статуса в случае если просто поставили на паузу

    if image.startswith('http'):
        if image.startswith('https://cdn.rcd.gg') and (active_activity['service'] in cache_image):
            thumb = BytesIO(cache_image[active_activity['service']])
            print(Fore.GREEN + 'Изображение загружено из кеша')
        else:
            async with ClientSession() as sess:
                try:
                    # пробуем загрузить плейсхолдер если его нет в кеше
                    thumb = await url_to_bytesio(active_activity['assets']['large_image'], sess)
                    print(Fore.BLUE + 'Изображение скачано...')
                    if image.startswith('https://cdn.rcd.gg'):
                        cache_image[active_activity['service']] = thumb.getvalue()
                        print(Fore.GREEN + '(Изображение загружено в кеш)')
                except (ClientResponseError, ClientConnectorError, gaierror):
                    thumb = None
                    print(f'{Fore.RED}{Style.BRIGHT}Возникла ошибка при скачивании изображения!{Style.RESET_ALL} {Fore.YELLOW}Статус будет загружен без обложки.')
    elif image.startswith('data'):
        print(Fore.YELLOW + 'Получено base64-изображение')
        _header, b64 = image.split(",", 1)
        data = b64decode(b64)
        thumb = BytesIO(data)
    else:
        thumb = None
        print(Fore.RED + Style.BRIGHT + 'Формат изображения не поддерживается программой! Сообщите об этом разработчику.')

    # обновляем кешированные данные если они отличаются от полученных
    cache_title = title
    cache_artist = artist

    sample = audio.tag_change(title, artist)
    await client.update_status(sample, thumb)

    return web.Response()

async def main():
    """
    Запуск всех необходимых модулей.

    пока что так, ибо если я начну сюда пихать всё остальное, я взорвусь
    """
    await client.start_client()
    print(Fore.BLUE + 'Telegram-клиент запущен...')

    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config['premid']['port'])
    await site.start() # запускаем прослууушкуууу
    
    print(f'{Fore.BLUE}Сервер запущен по адресу {Fore.LIGHTYELLOW_EX}http://localhost:{config['premid']['port']}{Fore.BLUE}, ожидание данных...')
    # держим событие в цикле
    try:
        while True:
            await asyncio.sleep(3600)
    except:
        try:
            print(f"{Fore.BLUE}Подчищаем за собой и отключаемся...")
            print(f"{Fore.YELLOW}(вы можете пропустить этот процесс, нажав на крестик ещё раз; учтите, что в этом случае статус вам придётся чистить вручную!)")
            await client.delete_status()
            await client.delete_cache()
        except:
            pass
    await client.stop_client()

if __name__ == "__main__":
    asyncio.run(main())
