'Окно "О программе".'
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("О программе | TRP")

        self.setWindowFlag(Qt.CustomizeWindowHint, True) # подсказка: окно можно кастомизировать!
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.setFixedSize(400, 175)
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        
        self.logo = QLabel(self)
        self.logo.setFixedSize(100, 100)
        self.logo.setPixmap(QPixmap("logo.png"))
        self.logo.setScaledContents(True)
        self.horizontalLayout.addWidget(self.logo)

        self.verticalLayout_3 = QVBoxLayout()

        self.title_version = QLabel(self)
        self.title_version.setTextFormat(Qt.TextFormat.MarkdownText)
        self.title_version.setText("**Telegram Rich Presence** *v0.1.0*")
        self.verticalLayout_3.addWidget(self.title_version)

        self.description = QLabel(self)
        self.description.setWordWrap(True)
        self.description.setText("Ваша активность в реальном времени внутри плейлиста в профиле")
        self.verticalLayout_3.addWidget(self.description)

        self.license = QLabel(self)
        self.license.setOpenExternalLinks(True)
        self.license.setTextFormat(Qt.TextFormat.MarkdownText)
        self.license.setText("Лицензия [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html)")
        self.verticalLayout_3.addWidget(self.license)

        self.repo = QLabel(self)
        self.repo.setWordWrap(True)
        self.repo.setOpenExternalLinks(True)
        self.repo.setTextFormat(Qt.TextFormat.MarkdownText)
        self.repo.setText("Исходный код, информация о контрибьюторах и использованных материалах на [GitHub](https://github.com/cheat-r/telegram-rich-presence)")
        self.verticalLayout_3.addWidget(self.repo)

        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.close_button = QPushButton(self)
        self.close_button.setMaximumSize(100, 100)
        self.close_button.setText("OK")

        self.verticalLayout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.close_button.clicked.connect(self.close)
        self.close_button.setDefault(True)
