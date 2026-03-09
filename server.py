"""
Сервер для получения запросов с PreMiD, а также связующее звено между всеми модулями.
"""
from io import BytesIO
from aiohttp import web, ClientResponseError, ClientConnectorError
from socket import gaierror
from client import Client
from tags import Audio
from utils import url_to_bytesio
from base64 import b64decode
from colorama import Fore, Back, Style

class Server:
    "Связующее звено между всеми классами."
    def __init__(self, client: Client, audio: Audio, config: dict = None):
        self.app = web.Application()
        self.routes = web.RouteTableDef()
        self.cache_title = self.cache_artist = None # так как premid отдаёт запрос на каждое действие (пауза и воспроизведение), то лучше не дёргать лишний раз телегу, нам же проще будет
        self.cache_image = {} # лишние запросы в сеть стараемся не делать, здесь будут сохраняться мини-превьюхи (они и так занимают мало места)
        self.client = client
        self.audio = audio
        if not config:
            self.port = 1225
        else:
            self.port = config['premid']['port']

    async def _sillyyou(self, request: web.Request): # GET /
        return web.Response(text='Если вы видите этот текст, TRP определённо работает!\nЗдесь вам нечего делать, ибо веб-сервер хостится не для вас, а для PreMiD (и возможных будущих расширений?).')

    async def _areyoukidding(self, request: web.Request): # GET /trp/premid
        return web.Response(text='Ваша любопытность крайне ценится, однако здесь вам нечего делать.')

    async def _premid(self, request: web.Request): # POST /trp/premid
        """
        Последовательность действий при получении запроса от PreMiD.
        """
        data = await request.json()
        active_activity = data['active_activity']

        if not active_activity:
            await self.client.delete_status() # удаляем статус, так как отсутствует активная активность
            return web.Response()
        
        if not 'details' in active_activity:
            print(Fore.LIGHTYELLOW_EX + 'Кажется, мы потеряли соединение с интернетом... Либо активность решила выпендриться и выкинуть пустые данные. Зараза.')
            await self.client.delete_status()
            return web.Response()
        
        title = f"{active_activity['details']}"

        if not 'state' in active_activity: # оказывается так тоже может быть???
            artist = f"{active_activity['service']}"
        else:
            artist = f"{active_activity['service']} | {active_activity['state']}"
        
        image = active_activity['assets']['large_image']
        
        if title == self.cache_title and artist == self.cache_artist:
            print(Fore.MAGENTA + 'Совпадение с предыдущим запросом!')
            return web.Response() # не делаем повторное обновление статуса в случае если просто поставили на паузу

        if image.startswith('http'):
            if image.startswith('https://cdn.rcd.gg') and (active_activity['service'] in self.cache_image):
                thumb = BytesIO(self.cache_image[active_activity['service']])
                print(Fore.GREEN + 'Изображение загружено из кеша')
            else:
                try:
                    # пробуем загрузить плейсхолдер если его нет в кеше
                    thumb = await url_to_bytesio(active_activity['assets']['large_image'])
                    print(Fore.BLUE + 'Изображение скачано...')
                    if image.startswith('https://cdn.rcd.gg'):
                        self.cache_image[active_activity['service']] = thumb.getvalue()
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
        self.cache_title = title
        self.cache_artist = artist

        sample = self.audio.tag_change(title, artist)
        await self.client.update_status(sample, thumb)

        return web.Response()
    
    async def start(self):
        "Запуск сервера со всеми прилегающими интеграциями."
        self.app.add_routes([web.post('/trp/premid', self._premid),
                             web.get('/trp/premid', self._areyoukidding),
                             web.get('/', self._sillyyou)])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
