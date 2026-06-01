"Окно настроек. Нейрощлоп - следует переписать."
import sys
import json
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QTreeWidget, 
    QTreeWidgetItem, QStackedWidget, QSplitter, QVBoxLayout, 
    QFormLayout, QLineEdit, QCheckBox, QSpinBox, QLabel, 
    QComboBox, QPushButton, QHBoxLayout, QMessageBox
)

class SettingsWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"
    
    def __init__(self):
        super().__init__()
        self.settings_data = {}
        self.settings_saved = False
        
        self.setWindowTitle("Настройки")
        self.resize(800, 500)

        self.pages = {}

        splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(220)

        self.stack = QStackedWidget()

        splitter.addWidget(self.tree)
        splitter.addWidget(self.stack)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)

        # Создаем область для кнопок
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("ОК")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        self.setCentralWidget(central)

        self.create_pages()
        self.create_tree()

        self.tree.currentItemChanged.connect(self.on_tree_item_changed)

        self.tree.expandAll()
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        
        # Загружаем сохраненные настройки
        self.load_settings()

    def add_page(self, key: str, title: str, widget: QWidget):
        """Добавляет страницу настроек в QStackedWidget"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title_label = QLabel(f"<h2>{title}</h2>")
        layout.addWidget(title_label)
        layout.addWidget(widget)
        layout.addStretch()

        index = self.stack.addWidget(page)
        self.pages[key] = index

    def create_pages(self):
        """Создает все страницы настроек. Изменил его - измени и другие!"""
        # Настройки приложения
        app_widget = QWidget()
        form = QFormLayout(app_widget)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский"])

        self.autostart_checkbox = QCheckBox("Запускать вместе с системой")

        form.addRow("Язык приложения:", self.language_combo)
        form.addRow("", self.autostart_checkbox)

        self.add_page("app", "Приложение", app_widget)

        # Сервер
        server_widget = QWidget()
        form = QFormLayout(server_widget)

        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(1, 65535)
        self.server_port_spin.setValue(1225)

        form.addRow("Порт сервера:", self.server_port_spin)
        form.addRow(QLabel("Порт, на котором будет работать внутренний сервер. Необходим для интеграции с PreMiD.", wordWrap=True))

        self.add_page("server", "Сервер", server_widget)

        # Прокси
        proxy_widget = QWidget()
        form = QFormLayout(proxy_widget)

        form.addRow(QSplitter(Qt.Horizontal))

        self.use_proxy_checkbox = QCheckBox("Включить прокси")

        self.proxy_host_edit = QLineEdit()
        self.proxy_port_spin = QSpinBox()
        self.proxy_key_edit = QLineEdit()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(443)

        form.addRow("Хост:", self.proxy_host_edit)
        form.addRow("Порт:", self.proxy_port_spin)
        form.addRow("Ключ:", self.proxy_key_edit)
        form.addRow("", self.use_proxy_checkbox)
        form.addRow(QLabel("Настройка MTProto для подключения к Telegram в странах, где доступ к нему блокируется.", wordWrap=True))


        self.add_page("proxy", "Прокси", proxy_widget)

        # Ключи доступа
        keys_widget = QWidget()
        form = QFormLayout(keys_widget)

        form.addRow(QLabel("Раздел с ключами доступа к вашему аккаунту в разных сервисах.\n\n**ВНИМАНИЕ!** Не делитесь ключами (и своим файлом конфигурации) НИ С КЕМ, так как злоумышленники могут получить доступ к вашим аккаунтам!", textFormat=Qt.TextFormat.MarkdownText, wordWrap=True))

        self.add_page("keys", "Ключи доступа", keys_widget)

        # Ключи доступа - Telegram
        keys_telegram_widget = QWidget()
        form = QFormLayout(keys_telegram_widget)

        form.addRow(QLabel("Зарегистрируйтесь в [my.telegram.org](https://my.telegram.org) и введите оттуда ваши ключи.\n\n**ВНИМАНИЕ!** Ключи невозможно перегенерировать, они выдаются на аккаунт лишь единожды. Будьте с ними максимально аккуратны!", textFormat=Qt.TextFormat.MarkdownText, openExternalLinks=True, wordWrap=True))
        
        self.api_id_spin = QSpinBox()
        self.api_hash_edit = QLineEdit()
        
        self.api_id_spin.setRange(0, 999999999)
        self.api_hash_edit.setPlaceholderText("l0ngStr1n6")

        form.addRow("api_id:", self.api_id_spin)
        form.addRow("api_hash:", self.api_hash_edit)
        
        self.add_page("keys_telegram", "Telegram", keys_telegram_widget)

        # О программе
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)

        layout.addWidget(QLabel("Пример окна настроек на PySide6."))
        layout.addWidget(QLabel("Версия: 1.0.0"))

        #self.add_page("about", "О программе", about_widget)

    def create_tree(self):
        """Создает дерево пунктов меню. Изменил его - измени и другие!"""
        app_item = QTreeWidgetItem(["Приложение"])
        app_item.setData(0, Qt.ItemDataRole.UserRole, "app")
        self.tree.addTopLevelItem(app_item)

        server_item = QTreeWidgetItem(["Сервер"])
        server_item.setData(0, Qt.ItemDataRole.UserRole, "server")
        self.tree.addTopLevelItem(server_item)

        proxy_item = QTreeWidgetItem(["Прокси"])
        proxy_item.setData(0, Qt.ItemDataRole.UserRole, "proxy")
        server_item.addChild(proxy_item)

        keys_item = QTreeWidgetItem(["Ключи доступа"])
        keys_item.setData(0, Qt.ItemDataRole.UserRole, "keys")
        self.tree.addTopLevelItem(keys_item)

        keys_telegram_item = QTreeWidgetItem(["Telegram"])
        keys_telegram_item.setData(0, Qt.ItemDataRole.UserRole, "keys_telegram")
        keys_item.addChild(keys_telegram_item)

    def on_tree_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        """Обработчик выбора пункта в дереве"""
        if current is None:
            return

        key = current.data(0, Qt.UserRole)

        if key in self.pages:
            self.stack.setCurrentIndex(self.pages[key])

    def load_settings(self):
        """Загрузка настроек из JSON файла. Если настроек нет, загружаются значения по умолчанию."""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.settings_data = json.load(f)
                
                self.apply_settings_to_widgets()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")

    def apply_settings_to_widgets(self):
        """Применяет загруженные настройки к виджетам. Изменил его - измени и другие!"""
        # Приложение
        app = self.settings_data["app"]
        index = self.language_combo.findText(app["language"])
        if index != -1:
            self.language_combo.setCurrentIndex(index)
        self.autostart_checkbox.setChecked(app["autostart"])

        # Сервер
        server = self.settings_data["server"]
        #self.timeout_spin.setValue(server["timeout"])

        # Прокси
        proxy = self.settings_data["proxy"]
        self.use_proxy_checkbox.setChecked(proxy["use_proxy"])
        self.proxy_host_edit.setText(proxy["proxy_host"])
        self.proxy_port_spin.setValue(proxy["proxy_port"])
        self.proxy_key_edit.setText(proxy["proxy_key"])

        # Ключи
        keys = self.settings_data["keys"]
        
        # Ключи - Телеграм
        keys_telegram = keys["telegram"]
        self.api_id_spin.setValue(keys_telegram["api_id"])
        self.api_hash_edit.setText(keys_telegram["api_hash"])

    def collect_settings_from_widgets(self):
        """Собирает настройки с виджетов в словарь. Изменил его - измени и другие!"""
        settings = {
            "app": {
                "language": self.language_combo.currentText(),
                "autostart": self.autostart_checkbox.isChecked()
            },
            "server": {
                "server_port": self.server_port_spin.value()
            },
            "proxy": {
                "use_proxy": self.use_proxy_checkbox.isChecked(),
                "proxy_host": self.proxy_host_edit.text().strip(),
                "proxy_port": self.proxy_port_spin.value(),
                "proxy_key": self.proxy_key_edit.text().strip()
            },
            "keys": {
                "comment": "Do not share this with anyone, as it contains sensitive data that can be used with bad intentions!",
                "telegram": {
                    "api_id": self.api_id_spin.value(),
                    "api_hash": self.api_hash_edit.text().strip()
                }
            }
        }
        return settings

    def save_settings(self):
        """Сохраняет настройки в JSON файл."""
        try:
            self.settings_data = self.collect_settings_from_widgets()
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, ensure_ascii=False, indent=2)
            self.settings_saved = True
            return True
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")
            return False

    def on_ok_clicked(self):
        if self.save_settings():
            self.close()

    def on_cancel_clicked(self):
        self.settings_saved = False
        self.close()

    def closeEvent(self, event: QCloseEvent):
        """Обработчик закрытия окна. Если настройки не были сохранены, при закрытии окна всплывёт месседжбокс о необходимости сохраниться."""
        if not self.settings_saved:
            reply = QMessageBox(self)
            reply.setWindowTitle("Подтверждение")
            reply.setText("Вы хотите сохранить изменения перед выходом?")
            reply.setIcon(QMessageBox.Question)

            btn_yes = reply.addButton("Да", QMessageBox.YesRole)
            btn_no = reply.addButton("Нет", QMessageBox.NoRole)
            btn_cancel = reply.addButton("Отмена", QMessageBox.RejectRole)
            reply.setDefaultButton(btn_yes)

            reply.setWindowFlag(Qt.CustomizeWindowHint, True)
            reply.setWindowFlag(Qt.WindowMinimizeButtonHint, False)

            reply.exec()

            if reply.clickedButton() == btn_yes:
                if not self.save_settings():
                    event.ignore()
            elif reply.clickedButton() == btn_no:
                event.accept()
            else:  # Отмена
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SettingsWindow()
    window.show()

    sys.exit(app.exec())