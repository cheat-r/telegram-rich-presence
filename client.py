"""
Работа с Telegram через кастомное приложение. Требует регистрации в [my.telegram.org](https://my.telegram.org).

Используются библиотеки [Telethon](https://docs.telethon.dev/) и [qrcode](https://github.com/lincolnloop/python-qrcode).
"""
import logging
from config import config
from utils import clear
from io import BytesIO
from qrcode import QRCode
from getpass import getpass
from telethon import TelegramClient, connection
from telethon.errors import SessionPasswordNeededError as SPNError
#from telethon.tl.functions.users import GetSavedMusicRequest
from telethon.tl.functions.account import SaveMusicRequest
from colorama import init, Fore, Back, Style

init(autoreset=True)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

config = config['telegram']

API_ID = config['api_id']
API_HASH = config['api_hash']

if config['proxy']['enabled']:
    client = TelegramClient('trp', API_ID, API_HASH, connection=connection.ConnectionTcpMTProxyRandomizedIntermediate, proxy=(config['proxy']['host'], config['proxy']['port'], config['proxy']['secret']), connection_retries=-1)
else:
    client = TelegramClient('trp', API_ID, API_HASH)
file = None # Чтобы не засорять чат, будет изменяться один файл и впоследствии удаляться
qr = QRCode()

def gen_qr(url):
    """
    Генерация QR-кода для авторизации.
    """
    clear()
    print(f"{Fore.LIGHTBLUE_EX}Отсканируйте данный QR-код через приложение (Настройки - Устройства - Подключить устройство):")
    qr.clear()
    qr.add_data(url)
    qr.print_ascii()

async def start_client():
    """
    Инициализация Telegram-клиента.
    
    Если нет активной сессии, инициализирует интерактивную авторизацию, в ином случае просто логинит.
    """
    await client.connect()
    if await client.is_user_authorized():
        return
    
    choice = input(f"{Fore.LIGHTYELLOW_EX}Выберите метод аутентификации:{Fore.WHITE}\n1) По QR-коду {Fore.LIGHTBLUE_EX}(по умолчанию){Fore.WHITE}\n2) По номеру телефона\n[{Style.BRIGHT}1{Style.RESET_ALL}/2]: ")
    while choice not in ["1", "2", ""]:
        choice = input(f"[{Style.BRIGHT}1{Style.RESET_ALL}/2]: ")
    if choice == "":
        choice = "1"
    choice = int(choice)
    if choice == 2:
        await client.start() # по номеру телефона
        return
    
    qr_login = await client.qr_login() # по qr-коду
    r = False
    while not r:
        gen_qr(qr_login.url)
        try:
            r = await qr_login.wait()
        except TimeoutError:
            await qr_login.recreate()
        except SPNError:
            clear()
            tfa = False
            r = True
            while tfa == False:
                pwd = getpass(f"{Fore.MAGENTA}Введите код двухфакторной аутентификации: ")
                try:
                    await client.sign_in(password=pwd)
                    tfa = True
                except Exception as e:
                    print(f"{Fore.RED}{Style.BRIGHT}Указан неверный пароль.{Style.NORMAL} {Fore.YELLOW}Повторите попытку.\n{Fore.RED}{e}\n")
    clear()

async def stop_client():
    """
    Остановка клиента. Наверное.
    """
    await client.disconnect()

async def update_status(sample: BytesIO, thumb = None):
    """
    Загрузка статуса и его обновление в профиле.
    """
    global file
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

    Запросу без разницы, есть ли файл в списке музыки или его там нет.
    
    Другое дело, когда файла вовсе нет...
    """
    global file
    print(Fore.BLUE + 'Удаление статуса...')
    if file is None:
        print(Fore.YELLOW + 'Удалять нечего, пропускаем')
        return
    await client(SaveMusicRequest(file, unsave=True))
    print(Fore.GREEN + 'Статус удалён')

async def delete_cache():
    """
    Удаление файла из избранных (если есть что удалять).
    
    Вы же не будете его там вечно хранить, так ведь?
    """
    global file
    print(Fore.BLUE + 'Удаление файла...')
    if file is None:
        print(Fore.YELLOW + 'Удалять нечего, пропускаем')
        return
    await file.delete()
    print(Fore.GREEN + 'Файл удалён')
