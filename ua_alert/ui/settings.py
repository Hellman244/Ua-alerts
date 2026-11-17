from PySide6.QtWidgets import QWidget,QFormLayout,QLineEdit,QSpinBox,QCheckBox,QPushButton,QSlider,QLabel,QHBoxLayout,QMessageBox,QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

class SettingsPage(QWidget):
    saved = Signal()
    def __init__(self, database, sound):
        super().__init__(); self.db=database; self.sound=sound
        page=QVBoxLayout(self); page.setContentsMargins(36,30,36,22); page.setSpacing(16)
        title=QLabel("Налаштування"); title.setObjectName("pageTitle"); page.addWidget(title)
        form=QFormLayout(); form.setSpacing(14); page.addLayout(form); page.addStretch(1)
        import keyring
        from ..services.secrets import get_api_token
        self.keyring=keyring; self.token=QLineEdit(get_api_token()); self.token.setEchoMode(QLineEdit.EchoMode.Password); self.token.setPlaceholderText("Токен застосунку Alerts.in.ua")
        self.reveal=QCheckBox("Показати токен"); self.reveal.toggled.connect(lambda v:self.token.setEchoMode(QLineEdit.EchoMode.Normal if v else QLineEdit.EchoMode.Password))
        wrap=QHBoxLayout(); wrap.addWidget(self.token); wrap.addWidget(self.reveal); form.addRow("Токен API",wrap)
        self.interval=QSpinBox(); self.interval.setRange(15,300); self.interval.setValue(int(database.get("refresh_interval","30"))); form.addRow("Інтервал оновлення (сек)",self.interval)
        self.sounds=QCheckBox("Звукові сповіщення"); self.sounds.setChecked(database.get("sounds","true")=="true"); form.addRow("Звук",self.sounds)
        self.volume=QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0,100); self.volume.setValue(int(database.get("volume","75"))); self.volume.valueChanged.connect(sound.set_volume); form.addRow("Гучність",self.volume)
        self.tray=QCheckBox("Згортати в системний трей при закритті"); self.tray.setChecked(database.get("minimize_to_tray","true")=="true"); form.addRow("Вікно",self.tray)
        save=QPushButton("Зберегти налаштування"); save.clicked.connect(self.save); form.addRow(save)
        tests=QHBoxLayout()
        for label,kind in (("БПЛА","drone"),("Ракетна","missile"),("Відбій","safe"),("Невідомо","unknown")):
            b=QPushButton(label); b.clicked.connect(lambda checked=False,k=kind:sound.play(k)); tests.addWidget(b)
        form.addRow("Перевірити звук",tests)
    def save(self):
        try:
            if self.token.text().strip(): self.keyring.set_password("UA Alert", "api_token", self.token.text().strip())
            else:
                try: self.keyring.delete_password("UA Alert", "api_token")
                except self.keyring.errors.PasswordDeleteError: pass
        except Exception as exc:
            QMessageBox.critical(self,"Сховище токенів недоступне",f"Не вдалося зберегти API-токен у системному сховищі. Перевірте службу системного сховища ключів і повторіть спробу.\n\n{exc}"); return
        for k,v in (("refresh_interval",self.interval.value()),("sounds",str(self.sounds.isChecked()).lower()),("volume",self.volume.value()),("minimize_to_tray",str(self.tray.isChecked()).lower())): self.db.set(k,v)
        self.sound.enabled=self.sounds.isChecked()
        self.saved.emit()
