"Меню трея."
from PySide6.QtGui import QIcon, QAction, QDesktopServices, QPixmap
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QCheckBox, QWidgetAction
from interface.about import AboutWindow
from interface.settings import MainWindow

class TrayMenu(QMenu):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

        # Установка иконки в трее
        self.tray_icon = QSystemTrayIcon(QIcon("logo.png"))
        self.tray_icon.setContextMenu(self)
        self.tray_icon.setToolTip("Telegram Rich Presence")

        # Статус в меню
        self.info_status = QAction("Информация о статусе...")
        self.info_status.setDisabled(True)
        self.addAction(self.info_status)

        # Чекбокс для вкл/выкл (ДА так надо чтоб при нажатии не вылетало из меню)
        self.toggle_status = QWidgetAction(self)
        self.check = QCheckBox("Включить статус")
        self.check.stateChanged.connect(self.toggle_func)
        self.toggle_status.setDefaultWidget(self.check)
        self.addAction(self.toggle_status)

        # Окно с настройками (WIP)
        self.config_status = QAction("Настройки...")
        self.config_status.triggered.connect(self.config_func)
        self.addAction(self.config_status)
        self.config_window = None
        self.about_window = None

        self.addSeparator()

        # Самопохвала (потому что кто если не я... хех...)
        self.link_action = QAction((QIcon("favicon.png")), "Сайт разработчика")
        self.link_action.triggered.connect(self.link_func)
        self.addAction(self.link_action)

        # Окно с "очень полезной" информацией
        self.about_action = QAction("О программе...")
        self.about_action.triggered.connect(self.about_func)
        self.addAction(self.about_action)

        self.quit_action = QAction("Выйти")
        self.quit_action.triggered.connect(self.app_quit)
        self.addAction(self.quit_action)

    def link_func(self):
        QDesktopServices.openUrl("https://killmyself.ru")

    def toggle_func(self, state):
        if state:
            self.tray_icon.setToolTip("Telegram Rich Presence\n[Активно]")
            self.info_status.setText("Статус включён")
        else:
            self.tray_icon.setToolTip("Telegram Rich Presence\n[Отключено]")
            self.info_status.setText("Статус выключен")
    
    def config_func(self):
        if self.config_window is None:
            self.config_window = MainWindow()
            # При закрытии окна обнулим ссылку
            self.config_window.destroyed.connect(lambda: setattr(self, "config_window", None))
        self.config_window.show()
        self.config_window.raise_()
        self.config_window.activateWindow()

    def about_func(self):
        if self.about_window is None:
            self.about_window = AboutWindow()
            self.about_window.destroyed.connect(lambda: setattr(self, "about_window", None))
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()

    def app_quit(self):
        print("Выход...")
        # выполнять всякое
        self.app.quit()
