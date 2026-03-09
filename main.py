"""
Основной файл. Через него запускаются все модули.
"""
import asyncio
from colorama import init, Fore, Back, Style

from config import config
from tags import Audio
from client import Client
from server import Server

audio = Audio()
client = Client(config)
server = Server(client, audio, config)

init(autoreset=True)

async def main():
    """
    Запуск всех необходимых модулей.

    пока что так, ибо если я начну сюда пихать всё остальное, я взорвусь
    """
    await client.start_client()
    print(Fore.BLUE + 'Telegram-клиент запущен...')
    await server.start()
    print(f'{Fore.BLUE}Сервер запущен по адресу {Fore.LIGHTYELLOW_EX}http://localhost:{config['premid']['port']}{Fore.BLUE}, ожидание данных...')
    # держим событие в цикле
    try:
        while True:
            await asyncio.sleep(3600)
    except:
        try:
            print(f"{Fore.BLUE}Подчищаем за собой и отключаемся...")
            print(f"{Fore.YELLOW}(вы можете пропустить этот процесс; учтите, что в этом случае статус вам придётся чистить вручную!)")
            await client.delete_status()
            await client.delete_cache()
        except:
            pass
    await client.stop_client()

if __name__ == "__main__":
    asyncio.run(main())
