"Модуль графического интерфейса. Пока временный."
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import sys, ctypes
from interface.tray import TrayMenu

# фигня чтоб в панели управления винды отображалась иконка
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("nya.cheat_r.trp")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.png"))
    app.setQuitOnLastWindowClosed(False)

    tray = TrayMenu(app)
    tray.tray_icon.show()

    sys.exit(app.exec())
