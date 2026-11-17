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
QWidget{background:#0a111a;color:#edf1f5;font-family:'Inter','Segoe UI',sans-serif;font-size:13px}
QWidget#shell{background:#0a111a}
QFrame#sidebar{background:#0c151f;border:1px solid #1e2b39;border-radius:16px}
QFrame#brandMark{background:#f1c40f;border-radius:10px}
QLabel#brandInitial{color:#fff;font-size:16px;font-weight:900}
QLabel#brandName{font-size:14px;font-weight:800;letter-spacing:1.5px;color:#f4f6f8}
QLabel#brandSub{color:#728092;font-size:9px;letter-spacing:1px}
QLabel#navCaption{color:#6f7d8d;font-size:9px;font-weight:700;letter-spacing:1.4px;padding:8px 11px 2px}
QPushButton#navButton{background:transparent;border:1px solid transparent;border-radius:9px;padding:11px 12px;color:#aab4c0;text-align:left;font-weight:600}
QPushButton#navButton:hover{background:#18212c;color:#fff}
QPushButton#navButton[active="true"]{background:#182431;border:1px solid #293c4e;border-left:3px solid #f1c40f;color:#fff}
QPushButton#navButton[active="true"]:hover{background:#263342}
QFrame#sidebarStatus{background:#151e28;border:1px solid #273340;border-radius:11px}
QLabel#sidebarSmall{color:#8491a0;font-size:10px}
QLabel#sidebarSafe{color:#4ec58a;font-size:11px;font-weight:700}
QFrame#panel,QFrame#statusPanel{background:#0e1721;border:1px solid #203041;border-radius:12px}
QFrame#insetPanel{background:#0b141e;border:1px solid #203041;border-radius:11px}
QFrame#metricCard{background:#0e1721;border:1px solid #203041;border-radius:12px}
QFrame#hero{background:#101820;border:1px solid #e1b70c;border-radius:14px}
QFrame#heroDivider{color:#293440}
QFrame#liveBadge{background:#111a22;border:1px solid #263441;border-radius:12px}
QLabel#pageTitle{font-size:27px;font-weight:750;color:#f3f5f7}
QLabel#eyebrow,QLabel#sectionEyebrow{color:#8492a2;font-size:9px;font-weight:750;letter-spacing:1.35px}
QLabel#clock{color:#aeb9c5;font-size:11px;font-weight:600;padding-left:16px}
QLabel#heroDot{font-size:24px}
QLabel#status{font-size:24px;font-weight:800}
QLabel#heroIcon{background:#101820}
QLabel#heroDetail{font-size:13px;color:#d5dce4}
QLabel#panelFootnote{font-size:10px;color:#9aa7b5}
QLabel#countBadge{background:#14212c;border:1px solid #283a4b;border-radius:8px;padding:5px 8px;color:#c0ccd8;font-size:9px;font-weight:700}
QLabel#modeBadgeDemo{background:#221f13;border:1px solid #e4b70a;border-radius:7px;padding:7px 10px;color:#f4ca21;font-size:10px;font-weight:800}
QLabel#modeBadgeLive{background:#10231d;border:1px solid #286549;border-radius:7px;padding:7px 10px;color:#63d39a;font-size:10px;font-weight:800}
QLabel#modeBadgePending,QLabel#modeBadgeUnknown{background:#151d26;border:1px solid #394653;border-radius:7px;padding:7px 10px;color:#aab6c2;font-size:10px;font-weight:800}
QLabel#selectorIcon{font-size:18px;color:#f1c40f}
QLabel#volumeValue{background:#101923;border:1px solid #465462;border-radius:6px;padding:5px 8px;color:#d8e0e8;font-size:10px}
QLabel#heroDetail{font-size:13px;color:#d5dce4}
QLabel#heroMeta{font-size:9px;color:#8492a2;font-weight:700;letter-spacing:1.2px}
QLabel#metricCaption{font-size:9px;color:#8290a0;font-weight:750;letter-spacing:1.1px}
QLabel#metricValue{font-size:20px;font-weight:750}
QLabel#sectionTitle{font-size:15px;font-weight:700;color:#eef2f6}
QLabel#secondaryText{font-size:11px;color:#a2adba}
QLabel#footerText{font-size:10px;color:#94a0ad}
QLabel#footerIcon{font-size:13px;color:#9aa8b7}
QPushButton{background:#121e2a;border:1px solid #293a4b;border-radius:8px;padding:9px 12px;color:#e8edf2;font-weight:600}
QPushButton:hover{background:#222e3a;border-color:#465568}
QPushButton:pressed{background:#2b3947}
QLineEdit,QComboBox,QSpinBox{background:#0c151e;border:1px solid #2a3b4d;border-radius:8px;padding:8px 10px;color:#edf1f5;selection-background-color:#b63c3b}
QComboBox::drop-down{border:0;width:24px}
QComboBox QAbstractItemView{background:#151e28;color:#edf1f5;border:1px solid #2a3642;selection-background-color:#303e4c}
QSlider::groove:horizontal{height:4px;background:#293541;border-radius:2px}
QSlider::handle:horizontal{background:#e54843;width:14px;margin:-5px 0;border-radius:7px}
QCheckBox{spacing:8px;color:#d4dbe2}
QCheckBox::indicator{width:16px;height:16px;border-radius:4px;background:#101720;border:1px solid #394653}
QCheckBox::indicator:checked{background:#d94b46;border-color:#d94b46}
QCheckBox#toggleCheck{background:#0d1721;border:0;border-bottom:1px solid #203041;padding:11px 2px;font-weight:600}
QCheckBox#toggleCheck::indicator{width:37px;height:20px;border:0;border-radius:10px;background:#34414d}
QCheckBox#toggleCheck::indicator:checked{background:#f1c40f}
QFrame#thinDivider{background:#21303d;max-height:1px}
QTableWidget,QListWidget{background:#0d131a;border:1px solid #25313d;border-radius:9px;gridline-color:#202b36;alternate-background-color:#111922;outline:0}
QListWidget#eventList{border:0;background:transparent}
QListWidget::item{padding:12px 8px;border-bottom:1px solid #1c2b39;color:#dce2e8}
QListWidget::item:selected{background:#1a2631;color:#fff;border-radius:6px}
QHeaderView::section{background:#151e28;padding:9px;border:0;color:#91a0af;font-size:10px;font-weight:700}
QScrollBar:vertical{width:8px;background:transparent;margin:3px}
QScrollBar::handle:vertical{background:#354352;border-radius:4px;min-height:24px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
"""

class MainWindow(QMainWindow):
    def __init__(self, db, token="", interval=30, simulation=False):
        super().__init__(); self.db=db; self.events=EventManager(db); self.sound=SoundService(__import__('pathlib').Path(__file__).resolve().parents[1], db.get("sounds","true")=="true")
        self.sound.set_volume(int(db.get("volume","75")))
        self.simulation=simulation
        self.setWindowTitle("Тривога — Моніторинг сповіщень" + (" [ДЕМО — НЕ РЕАЛЬНІ ДАНІ]" if simulation else "")); self.resize(1440,900); self.setMinimumSize(1100,720); self.setStyleSheet(STYLE)
        root=QWidget(); root.setObjectName("shell"); layout=QHBoxLayout(root); layout.setContentsMargins(14,14,14,14); layout.setSpacing(14)
        sidebar=QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(205)
        nav=QVBoxLayout(sidebar); nav.setContentsMargins(12,16,12,14); nav.setSpacing(6)
        brand_row=QHBoxLayout(); mark=QFrame(); mark.setObjectName("brandMark"); mark.setFixedSize(34,34); mark_layout=QVBoxLayout(mark); mark_layout.setContentsMargins(0,0,0,0); initial=QLabel("!"); initial.setObjectName("brandInitial"); initial.setAlignment(Qt.AlignmentFlag.AlignCenter); mark_layout.addWidget(initial)
        brand_text=QVBoxLayout(); brand=QLabel("ТРИВОГА"); brand.setObjectName("brandName"); brand_sub=QLabel("МОНІТОРИНГ"); brand_sub.setObjectName("brandSub"); brand_text.addWidget(brand); brand_text.addWidget(brand_sub); brand_row.addWidget(mark); brand_row.addLayout(brand_text); brand_row.addStretch(); nav.addLayout(brand_row)
        nav.addSpacing(28); caption=QLabel("НАВІГАЦІЯ"); caption.setObjectName("navCaption"); nav.addWidget(caption)
        self.stack=QStackedWidget(); self.dashboard=Dashboard(db,simulation); self.map_page=MapPage(); self.history=HistoryPage(db); self.settings=SettingsPage(db,self.sound)
        self.nav_buttons=[]
        for text,index,icon in (("Огляд",0,"⌂"),("Карта",1,"⌖"),("Історія",2,"◷"),("Налаштування",3,"⚙")):
            b=QPushButton(f"{icon}    {text}"); b.setObjectName("navButton"); b.setProperty("active",index==0); b.clicked.connect(lambda checked=False,i=index:self.select_page(i)); nav.addWidget(b); self.nav_buttons.append(b)
        nav.addStretch()
        status_card=QFrame(); status_card.setObjectName("sidebarStatus"); sb=QVBoxLayout(status_card); sb.setContentsMargins(11,11,11,11); small=QLabel("СТАН МОНІТОРИНГУ"); small.setObjectName("sidebarSmall"); self.sidebar_status=QLabel("●  Підключення…"); self.sidebar_status.setObjectName("sidebarSafe"); sb.addWidget(small); sb.addWidget(self.sidebar_status); nav.addWidget(status_card)
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
        alerts, stamp=result; self.last_success=stamp; self.sidebar_status.setText("●  Зв’язок активний"); self.sidebar_status.setStyleSheet("color:#4ec58a;font-size:11px;font-weight:700"); self.map_page.set_states(self.dashboard.states); self.db.set("unknown_notified","false"); changes=self.events.update(alerts); self.dashboard.set_data(alerts,True,stamp.astimezone().strftime("%d.%m.%Y  %H:%M:%S %Z")); self.map_page.set_states(self.dashboard.states); self.history.refresh(); self.tray.setToolTip("Тривога · дані оновлено")
        for region,old,new,alert in changes:
            kind="missile" if "MISSILE" in new else "drone" if "DRONE" in new else "safe" if new=="SAFE" else "unknown"
            self.sound.play(kind)
            if self.db.get("notifications","true")=="true": self.notifications.show(f"Тривога · {self.dashboard._translate_status(new)}",f"{region} · {alert.started_at if alert else 'Тривогу завершено'}")
    def on_failure(self, message):
        self.sidebar_status.setText("●  Немає зв’язку"); self.sidebar_status.setStyleSheet("color:#ef625d;font-size:11px;font-weight:700")
        self.dashboard.set_unknown(f"Немає зв’язку: {message}. Очікуємо повторне підключення."); self.map_page.set_states(self.dashboard.states); self.tray.setToolTip("Тривога · статус невідомий")
        if self.db.get("unknown_notified","false")!="true":
            self.sound.play("unknown");
            if self.db.get("notifications","true")=="true": self.notifications.show("Тривога · статус невідомий","Зв’язок із джерелом втрачено. Дані слід вважати застарілими.")
            self.db.set("unknown_notified","true")
    def check_stale(self):
        if self.last_success and (datetime.now().astimezone()-self.last_success.astimezone()).total_seconds()>120:
            self.dashboard.set_unknown("Дані застаріли. Останнє успішне оновлення: "+self.last_success.astimezone().strftime("%H:%M:%S"))
            self.map_page.set_states(self.dashboard.states)
            self.sidebar_status.setText("●  Дані застаріли")
            self.sidebar_status.setStyleSheet("color:#ef625d;font-size:11px;font-weight:700")
    def closeEvent(self,event):
        if self.db.get("minimize_to_tray","true")=="true": event.ignore(); self.hide()
        else: self.shutdown(); event.accept()
    def shutdown(self):
        if self.monitor and self.monitor.isRunning(): self.monitor.stop()
        self.tray.hide(); self.db.close()
