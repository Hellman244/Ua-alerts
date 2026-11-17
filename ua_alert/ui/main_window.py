from datetime import datetime
from PySide6.QtWidgets import QMainWindow,QWidget,QFrame,QLabel,QHBoxLayout,QVBoxLayout,QPushButton,QStackedWidget,QSystemTrayIcon,QMenu,QApplication
from PySide6.QtCore import QTimer, Qt
from .dashboard import Dashboard
from .map_page import MapPage
from .history import HistoryPage
from .settings import SettingsPage
from ..core.event_manager import EventManager
from ..services.sound_service import SoundService
from ..services.notification_service import NotificationService

STYLE="""
QWidget{background:#0d0d0f;color:#e8e8ea;font-family:'Inter','Segoe UI',sans-serif;font-size:13px}
QWidget#shell{background:#0d0d0f}
QFrame#sidebar{background:transparent;border:0;border-right:1px solid #1c1c20;border-radius:0}
QLabel#brandName{font-size:14px;font-weight:600;letter-spacing:0.5px;color:#e8e8ea}
QPushButton#navButton{background:transparent;border:0;border-radius:6px;padding:9px 10px;color:#8a8a90;text-align:left;font-weight:500}
QPushButton#navButton:hover{background:#151518;color:#e8e8ea}
QPushButton#navButton[active="true"]{background:#18181c;color:#ffffff}
QFrame#sidebarStatus{background:transparent;border:0}
QLabel#sidebarSmall{color:#6b6b72;font-size:11px}
QLabel#sidebarSafe{color:#8a8a90;font-size:12px;font-weight:500}
QFrame#panel,QFrame#statusPanel{background:transparent;border:0;border-top:1px solid #1c1c20;border-radius:0}
QFrame#heroPanel{background:transparent;border:0}
QFrame#hero{background:transparent;border:0}
QFrame#thinDivider{background:#1c1c20;max-height:1px;border:0}
QLabel#pageTitle{font-size:24px;font-weight:600;color:#f2f2f4}
QLabel#eyebrow,QLabel#sectionEyebrow{color:#6b6b72;font-size:12px;font-weight:400}
QLabel#clock{color:#6b6b72;font-size:12px;padding-left:16px}
QLabel#status{font-size:34px;font-weight:600}
QLabel#heroIcon{background:transparent}
QLabel#heroDetail{font-size:13px;color:#a0a0a8}
QLabel#panelFootnote{font-size:11px;color:#6b6b72}
QLabel#countBadge{background:transparent;border:0;color:#8a8a90;font-size:12px}
QLabel#modeBadgeDemo{background:transparent;border:0;padding:0;color:#d1a63a;font-size:12px}
QLabel#modeBadgeLive{background:transparent;border:0;padding:0;color:#4caf82;font-size:12px}
QLabel#modeBadgePending,QLabel#modeBadgeUnknown{background:transparent;border:0;padding:0;color:#8a8a90;font-size:12px}
QLabel#volumeValue{background:transparent;border:0;color:#8a8a90;font-size:12px}
QLabel#sectionTitle{font-size:14px;font-weight:600;color:#e8e8ea}
QLabel#secondaryText{font-size:12px;color:#8a8a90}
QLabel#footerText{font-size:11px;color:#5c5c63}
QPushButton{background:transparent;border:1px solid #2a2a2f;border-radius:6px;padding:8px 14px;color:#e8e8ea;font-weight:500}
QPushButton:hover{background:#18181c;border-color:#3a3a40}
QPushButton:pressed{background:#202026}
QLineEdit,QComboBox,QSpinBox{background:transparent;border:0;border-bottom:1px solid #2a2a2f;border-radius:0;padding:7px 2px;color:#e8e8ea;selection-background-color:#3a3a40}
QLineEdit:focus,QComboBox:focus,QSpinBox:focus{border-bottom:1px solid #e8e8ea}
QComboBox::drop-down{border:0;width:20px}
QComboBox QAbstractItemView{background:#151518;color:#e8e8ea;border:1px solid #2a2a2f;selection-background-color:#24242a;outline:0}
QSlider::groove:horizontal{height:2px;background:#2a2a2f;border-radius:1px}
QSlider::sub-page:horizontal{background:#e8e8ea;border-radius:1px}
QSlider::handle:horizontal{background:#ffffff;width:12px;margin:-5px 0;border-radius:6px}
QCheckBox{spacing:8px;color:#d0d0d5}
QCheckBox::indicator{width:16px;height:16px;border-radius:4px;background:transparent;border:1px solid #3a3a40}
QCheckBox::indicator:checked{background:#e8e8ea;border-color:#e8e8ea}
QTableWidget,QListWidget{background:transparent;border:0;gridline-color:#1c1c20;alternate-background-color:transparent;outline:0}
QListWidget#eventList{border:0;background:transparent}
QListWidget::item{padding:11px 4px;border-bottom:1px solid #1c1c20;color:#d0d0d5}
QListWidget::item:selected{background:#151518;color:#fff}
QHeaderView::section{background:transparent;padding:9px 4px;border:0;border-bottom:1px solid #1c1c20;color:#6b6b72;font-size:11px;font-weight:500}
QScrollBar:vertical{width:6px;background:transparent;margin:2px}
QScrollBar::handle:vertical{background:#2a2a2f;border-radius:3px;min-height:24px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
"""

class MainWindow(QMainWindow):
    def __init__(self, db, token="", interval=30, simulation=False):
        super().__init__(); self.db=db; self.events=EventManager(db); self.sound=SoundService(__import__('pathlib').Path(__file__).resolve().parents[1], db.get("sounds","true")=="true")
        self.sound.set_volume(int(db.get("volume","75")))
        self.simulation=simulation
        self.setWindowTitle("Тривога — Моніторинг сповіщень" + (" [ДЕМО — НЕ РЕАЛЬНІ ДАНІ]" if simulation else "")); self.resize(1440,900); self.setMinimumSize(1100,720); self.setStyleSheet(STYLE)
        root=QWidget(); root.setObjectName("shell"); layout=QHBoxLayout(root); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        sidebar=QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(190)
        nav=QVBoxLayout(sidebar); nav.setContentsMargins(16,24,16,20); nav.setSpacing(6)
        brand_row=QHBoxLayout(); brand=QLabel("Тривога"); brand.setObjectName("brandName"); brand_row.addWidget(brand); brand_row.addStretch(); nav.addLayout(brand_row)
        nav.addSpacing(24)
        self.stack=QStackedWidget(); self.dashboard=Dashboard(db,simulation); self.map_page=MapPage(); self.history=HistoryPage(db); self.settings=SettingsPage(db,self.sound)
        self.nav_buttons=[]
        for text,index in (("Огляд",0),("Карта",1),("Історія",2),("Налаштування",3)):
            b=QPushButton(text); b.setObjectName("navButton"); b.setProperty("active",index==0); b.clicked.connect(lambda checked=False,i=index:self.select_page(i)); nav.addWidget(b); self.nav_buttons.append(b)
        nav.addStretch()
        status_card=QFrame(); status_card.setObjectName("sidebarStatus"); sb=QVBoxLayout(status_card); sb.setContentsMargins(2,0,0,0); small=QLabel("Стан"); small.setObjectName("sidebarSmall"); self.sidebar_status=QLabel("Підключення…"); self.sidebar_status.setObjectName("sidebarSafe"); sb.addWidget(small); sb.addWidget(self.sidebar_status); nav.addWidget(status_card)
        layout.addWidget(sidebar); self.stack.addWidget(self.dashboard); self.stack.addWidget(self.map_page); self.stack.addWidget(self.history); self.stack.addWidget(self.settings); layout.addWidget(self.stack,1); self.setCentralWidget(root)
        self.tray=QSystemTrayIcon(self); self.tray.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)); menu=QMenu()
        menu.addAction("Відкрити панель",self.showNormal); menu.addAction("Увімкнути / вимкнути сповіщення",self.toggle_notifications); menu.addSeparator(); menu.addAction("Вийти",QApplication.instance().quit)
        self.tray.setContextMenu(menu); self.tray.setToolTip("Тривога · статус невідомий"); self.tray.activated.connect(lambda reason:self.showNormal() if reason==QSystemTrayIcon.ActivationReason.Trigger else None); self.tray.show(); self.notifications=NotificationService(self.tray)
        self.monitor=None; self.last_success=None; self.stale_timer=QTimer(self); self.stale_timer.timeout.connect(self.check_stale); self.stale_timer.start(5000)
        self.clock_timer=QTimer(self); self.clock_timer.timeout.connect(lambda:self.dashboard.clock.setText(datetime.now().astimezone().strftime("%Y-%m-%d  %H:%M:%S %Z"))); self.clock_timer.start(1000)
        self.settings.saved.connect(self.restart_monitor)
        self.dashboard.sounds_changed.connect(self.set_quick_sounds)
        self.dashboard.notifications_changed.connect(lambda enabled:self.db.set("notifications",str(enabled).lower()))
        self.dashboard.volume_changed.connect(self.set_quick_volume)
        self.map_page.region_selected.connect(self.show_region)
        self.start_monitor(token, interval)
    def set_quick_sounds(self, enabled):
        self.db.set("sounds",str(enabled).lower()); self.sound.enabled=enabled; self.settings.sounds.setChecked(enabled)
    def toggle_notifications(self):
        enabled=self.db.get("notifications","true")!="true"
        self.db.set("notifications",str(enabled).lower())
        self.dashboard.notify_toggle.setChecked(enabled)
    def set_quick_volume(self, value):
        self.db.set("volume",value); self.sound.set_volume(value); self.settings.volume.setValue(value)
    def show_region(self, name):
        self.select_page(0)
        self.dashboard.region.setCurrentText(name)
    def select_page(self,index):
        self.stack.setCurrentIndex(index)
        for i,button in enumerate(self.nav_buttons): button.setProperty("active",i==index); button.style().unpolish(button); button.style().polish(button)
    def start_monitor(self, token, interval):
        if self.monitor and self.monitor.isRunning(): self.monitor.stop()
        from ..core.alert_monitor import MonitorThread
        self.monitor=MonitorThread(token,interval,simulation=self.simulation); self.monitor.snapshot.connect(self.on_snapshot); self.monitor.failure.connect(self.on_failure); self.monitor.start()
    def restart_monitor(self):
        from ..services.secrets import get_api_token
        self.start_monitor(get_api_token(),self.settings.interval.value())
    def on_snapshot(self, result):
        alerts, stamp=result; self.last_success=stamp; self.sidebar_status.setText("Зв’язок активний"); self.sidebar_status.setStyleSheet("color:#4caf82;font-size:12px;font-weight:500"); self.map_page.set_states(self.dashboard.states); self.db.set("unknown_notified","false"); changes=self.events.update(alerts); self.dashboard.set_data(alerts,True,stamp.astimezone().strftime("%d.%m.%Y  %H:%M:%S %Z")); self.map_page.set_states(self.dashboard.states); self.history.refresh(); self.tray.setToolTip("Тривога · дані оновлено")
        for region,old,new,alert in changes:
            kind="missile" if "MISSILE" in new else "drone" if "DRONE" in new else "safe" if new=="SAFE" else "unknown"
            self.sound.play(kind)
            if self.db.get("notifications","true")=="true": self.notifications.show(f"Тривога · {self.dashboard._translate_status(new)}",f"{region} · {alert.started_at if alert else 'Тривогу завершено'}")
    def on_failure(self, message):
        self.sidebar_status.setText("Немає зв’язку"); self.sidebar_status.setStyleSheet("color:#e5534b;font-size:12px;font-weight:500")
        self.dashboard.set_unknown(f"Немає зв’язку: {message}. Очікуємо повторне підключення."); self.map_page.set_states(self.dashboard.states); self.tray.setToolTip("Тривога · статус невідомий")
        if self.db.get("unknown_notified","false")!="true":
            self.sound.play("unknown");
            if self.db.get("notifications","true")=="true": self.notifications.show("Тривога · статус невідомий","Зв’язок із джерелом втрачено. Дані слід вважати застарілими.")
            self.db.set("unknown_notified","true")
    def check_stale(self):
        if self.last_success and (datetime.now().astimezone()-self.last_success.astimezone()).total_seconds()>120:
            self.dashboard.set_unknown("Дані застаріли. Останнє успішне оновлення: "+self.last_success.astimezone().strftime("%H:%M:%S"))
            self.map_page.set_states(self.dashboard.states)
            self.sidebar_status.setText("Дані застаріли")
            self.sidebar_status.setStyleSheet("color:#e5534b;font-size:12px;font-weight:500")
    def closeEvent(self,event):
        if self.db.get("minimize_to_tray","true")=="true": event.ignore(); self.hide()
        else: self.shutdown(); event.accept()
    def shutdown(self):
        if self.monitor and self.monitor.isRunning(): self.monitor.stop()
        self.tray.hide(); self.db.close()
