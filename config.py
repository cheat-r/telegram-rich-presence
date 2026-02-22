"""
Конфигурация программы.

Так как это прототип, на данный момент файл приходится редактировать вручную, к тому же он помещается в корневую папку программы. Как-нибудь в будущем *моооожет* исправлю.
"""
import json, os
from utils import pause
    
if os.path.exists("config.json"):
    with open("config.json") as f:
        config = json.load(f)
else:
    config = {
        "comment": "Do not share this file with anyone, as it contains sensitive data and can be used with bad intentions!",
        "telegram": {
            "api_id": 0,
            "api_hash": "0",
            "proxy": {
                "enabled": False,
                "host": "",
                "port": 443,
                "secret": ""
            }
        },
        "premid": {
            "port": 1225
        }
    }

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\nЗаполните файл конфигурации и перезапустите программу.\nСамое минимальное, что потребуется заполнить - api_id и api_hash; остальное изменять необязательно.\nПолучить их можно на https://my.telegram.org.\n")
    pause()
    exit()
