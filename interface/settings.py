"Окно настроек."
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестовое окно")

        # Виджет для вывода логов
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # Кнопки для тестирования конфигурации
        self.test1 = QPushButton("Пустить ядерку")
        self.test2 = QPushButton("Отрубить пальцы")

        # Сборка интерфейса
        layout = QVBoxLayout()
        layout.addWidget(self.log)
        layout.addWidget(self.test1)
        layout.addWidget(self.test2)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)
