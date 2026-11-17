from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon

class NotificationService:
    def __init__(self, tray: QSystemTrayIcon): self.tray = tray
    def show(self, title, message):
        if QSystemTrayIcon.supportsMessages(): self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 10000)
