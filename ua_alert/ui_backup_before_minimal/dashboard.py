from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QComboBox, QListWidget, QCheckBox, QSlider, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from ..config import REGIONS
from .map_widget import COLORS


class SwitchCheckBox(QCheckBox):
    """Accessible checkbox drawn as the compact switch used in the reference UI."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(46)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        text_rect = self.rect().adjusted(0, 0, -56, 0)
        painter.setPen(QColor("#e2e8ee" if self.isEnabled() else "#77818b"))
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter) | int(Qt.TextFlag.TextWordWrap), self.text())
        track = self.rect().adjusted(self.width() - 46, (self.height() - 22) // 2,
                                     -4, -((self.height() - 22) // 2))
        track_color = QColor("#f1c40f" if self.isChecked() else "#34414d")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, 11, 11)
        knob_x = track.right() - 19 if self.isChecked() else track.left() + 3
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(knob_x, track.top() + 3, 16, 16)


class Dashboard(QWidget):
    sounds_changed = Signal(bool)
    notifications_changed = Signal(bool)
    volume_changed = Signal(int)

    def __init__(self, database, simulation=False):
        super().__init__()
        self.db = database
        self.simulation = simulation
        self.states = {name: "UNKNOWN" for _, name, _ in REGIONS}
        self.alerts = ()
        self.feed_unknown = True

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 18)
        root.setSpacing(16)

        header = QHBoxLayout()
        title_block = QVBoxLayout()
        self.page_title = QLabel("Моніторинг сповіщень")
        self.page_title.setObjectName("pageTitle")
        subtitle = QLabel("ПОТОЧНА СИТУАЦІЯ  ·  УКРАЇНА")
        subtitle.setObjectName("eyebrow")
        title_block.addWidget(self.page_title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block)
        header.addStretch()
        self.mode_badge = QLabel("ДЕМО-ДАНІ  ·  НЕ В РЕАЛЬНОМУ ЧАСІ" if simulation else "◌  ПІДКЛЮЧЕННЯ  ·  ALERTS.IN.UA")
        self.mode_badge.setObjectName("modeBadgeDemo" if simulation else "modeBadgePending")
        header.addWidget(self.mode_badge)
        self.clock = QLabel("—")
        self.clock.setObjectName("clock")
        header.addWidget(self.clock)
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(14)
        main_column = QVBoxLayout()
        main_column.setSpacing(12)

        status_panel = QFrame()
        status_panel.setObjectName("statusPanel")
        panel_layout = QVBoxLayout(status_panel)
        panel_layout.setContentsMargins(17, 13, 17, 13)
        panel_layout.setSpacing(8)
        panel_label = QLabel("ПОТОЧНЕ СПОВІЩЕННЯ")
        panel_label.setObjectName("sectionEyebrow")
        panel_layout.addWidget(panel_label)

        self.hero = QFrame()
        self.hero.setObjectName("hero")
        hero_row = QHBoxLayout(self.hero)
        hero_row.setContentsMargins(18, 16, 18, 15)
        hero_row.setSpacing(16)
        self.hero_icon = QLabel("◉")
        self.hero_icon.setObjectName("heroIcon")
        self.hero_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_icon.setFixedSize(76, 76)
        hero_row.addWidget(self.hero_icon)
        details = QVBoxLayout()
        details.setSpacing(7)
        self.status = QLabel("НЕВІДОМО")
        self.status.setObjectName("status")
        details.addWidget(self.status)
        selector_row = QHBoxLayout()
        selector_mark = QLabel("⌖")
        selector_mark.setObjectName("selectorIcon")
        selector_row.addWidget(selector_mark)
        self.region = QComboBox()
        self.region.addItem("Вся Україна")
        self.region.addItems([uk for _, uk, _ in REGIONS])
        self.region.currentTextChanged.connect(self.render_status)
        selector_row.addWidget(self.region, 1)
        details.addLayout(selector_row)
        self.alert_time = QLabel("Очікування першого успішного оновлення")
        self.alert_time.setObjectName("heroDetail")
        details.addWidget(self.alert_time)
        hero_row.addLayout(details, 1)
        panel_layout.addWidget(self.hero)
        info_row = QHBoxLayout()
        info = QLabel("ⓘ   Статус відображає лише дані, отримані від джерела сповіщень")
        info.setObjectName("panelFootnote")
        info_row.addWidget(info)
        info_row.addStretch()
        self.updated = QLabel("ОСТАННЄ ОНОВЛЕННЯ  —")
        self.updated.setObjectName("panelFootnote")
        info_row.addWidget(self.updated)
        panel_layout.addLayout(info_row)
        main_column.addWidget(status_panel)

        history_panel = QFrame()
        history_panel.setObjectName("statusPanel")
        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(17, 13, 17, 14)
        history_layout.setSpacing(10)
        history_head = QHBoxLayout()
        history_title = QLabel("Історія сповіщень")
        history_title.setObjectName("sectionTitle")
        history_head.addWidget(history_title)
        history_head.addStretch()
        self.active_count = QLabel("0 АКТИВНИХ")
        self.active_count.setObjectName("countBadge")
        history_head.addWidget(self.active_count)
        history_layout.addLayout(history_head)
        self.events = QListWidget()
        self.events.setObjectName("eventList")
        history_layout.addWidget(self.events, 1)
        self.history_hint = QLabel("Нові події з’являться тут після оновлення даних")
        self.history_hint.setObjectName("panelFootnote")
        history_layout.addWidget(self.history_hint)
        main_column.addWidget(history_panel, 1)
        content.addLayout(main_column, 7)

        side_column = QVBoxLayout()
        side_column.setSpacing(14)
        controls = QFrame()
        controls.setObjectName("statusPanel")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(16, 14, 16, 16)
        controls_layout.setSpacing(12)
        control_title = QLabel("Налаштування сповіщень")
        control_title.setObjectName("sectionTitle")
        controls_layout.addWidget(control_title)
        self.sound_toggle = SwitchCheckBox("Звукові сповіщення")
        self.sound_toggle.setObjectName("toggleCheck")
        self.sound_toggle.setChecked(database.get("sounds", "true") == "true")
        self.sound_toggle.toggled.connect(self.sounds_changed.emit)
        controls_layout.addWidget(self.sound_toggle)
        self.notify_toggle = SwitchCheckBox("Сповіщення на робочому столі")
        self.notify_toggle.setObjectName("toggleCheck")
        self.notify_toggle.setChecked(database.get("notifications", "true") == "true")
        self.notify_toggle.toggled.connect(self.notifications_changed.emit)
        controls_layout.addWidget(self.notify_toggle)
        separator = QFrame()
        separator.setObjectName("thinDivider")
        controls_layout.addWidget(separator)
        volume_head = QHBoxLayout()
        volume_label = QLabel("Гучність")
        volume_label.setObjectName("secondaryText")
        self.volume_value = QLabel(database.get("volume", "75") + "%")
        self.volume_value.setObjectName("volumeValue")
        volume_head.addWidget(volume_label)
        volume_head.addStretch()
        volume_head.addWidget(self.volume_value)
        controls_layout.addLayout(volume_head)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(int(database.get("volume", "75")))
        self.volume.valueChanged.connect(self._volume_changed)
        controls_layout.addWidget(self.volume)
        side_column.addWidget(controls)

        legend = QFrame()
        legend.setObjectName("statusPanel")
        legend_layout = QVBoxLayout(legend)
        legend_layout.setContentsMargins(16, 14, 16, 16)
        legend_layout.setSpacing(12)
        legend_title = QLabel("Легенда статусів")
        legend_title.setObjectName("sectionTitle")
        legend_layout.addWidget(legend_title)
        for status, title, description in (
            ("DRONE DANGER", "ЗАГРОЗА БПЛА", "Джерело явно вказує загрозу БПЛА"),
            ("MISSILE / BOMBING DANGER", "РАКЕТНА / БОМБОВА НЕБЕЗПЕКА", "Явно вказана ракетна або бомбова загроза"),
            ("SAFE", "ВІДБІЙ / БЕЗ АКТИВНИХ ТРИВОГ", "Активні сповіщення не отримані"),
            ("UNKNOWN", "НЕВІДОМО", "Дані застаріли або недоступні"),
        ):
            item = QVBoxLayout()
            title_label = QLabel("●   " + title)
            title_label.setStyleSheet(f"color:{COLORS[status]};font-size:10px;font-weight:800")
            desc = QLabel(description)
            desc.setObjectName("secondaryText")
            desc.setWordWrap(True)
            item.addWidget(title_label)
            item.addWidget(desc)
            legend_layout.addLayout(item)
        side_column.addWidget(legend, 1)
        content.addLayout(side_column, 4)
        root.addLayout(content, 1)

        warning = QLabel("UA Alert — допоміжний інформаційний засіб. Він не замінює офіційні сповіщення про повітряну тривогу, екстрені служби, сирени чи вказівки української влади. Завжди дотримуйтеся офіційних інструкцій.")
        warning.setObjectName("footerText")
        warning.setWordWrap(True)
        root.addWidget(warning)

    def _volume_changed(self, value):
        self.volume_value.setText(f"{value}%")
        self.volume_changed.emit(value)

    def set_data(self, alerts, connected, updated):
        self.feed_unknown = not connected
        self.alerts = alerts
        self.states = {
            name: next((a.classification for a in alerts if a.region == name), "SAFE")
            for _, name, _ in REGIONS
        }
        active = len(alerts)
        self.active_count.setText(f"{active} АКТИВНИХ")
        self.updated.setText(f"ОСТАННЄ ОНОВЛЕННЯ  {updated}")
        if self.simulation:
            self.mode_badge.setText("ДЕМО-ДАНІ  ·  НЕ В РЕАЛЬНОМУ ЧАСІ")
        elif connected:
            self.mode_badge.setText("●  ДАНІ LIVE  ·  ALERTS.IN.UA")
            if self.mode_badge.objectName() != "modeBadgeLive":
                self.mode_badge.setObjectName("modeBadgeLive")
                self.mode_badge.style().unpolish(self.mode_badge)
                self.mode_badge.style().polish(self.mode_badge)
        self.events.clear()
        if not alerts:
            self.events.addItem("✓   Активних сповіщень не отримано")
        for alert in alerts:
            start_time = alert.started_at or "Час початку відсутній"
            self.events.addItem(f"●   {self._translate_status(alert.classification)}\n      {alert.region}   ·   {start_time}")
        self.render_status()

    def set_unknown(self, message):
        self.feed_unknown = True
        self.states = {name: "UNKNOWN" for _, name, _ in REGIONS}
        self.active_count.setText("СТАН НЕВІДОМИЙ")
        self.updated.setText("ОСТАННЄ ОНОВЛЕННЯ  ЗВ’ЯЗОК ВІДСУТНІЙ")
        if not self.simulation:
            self.mode_badge.setText("●  ЗВ’ЯЗОК ВІДСУТНІЙ  ·  СТАТУС НЕВІДОМИЙ")
            if self.mode_badge.objectName() != "modeBadgeUnknown":
                self.mode_badge.setObjectName("modeBadgeUnknown")
                self.mode_badge.style().unpolish(self.mode_badge)
                self.mode_badge.style().polish(self.mode_badge)
        self.events.clear()
        self.events.addItem("◌   Дані недоступні — активний стан не підтверджено")
        self.render_status(message)

    @staticmethod
    def _translate_status(status):
        return {
            "DRONE DANGER": "ЗАГРОЗА БПЛА",
            "MISSILE / BOMBING DANGER": "РАКЕТНА / БОМБОВА НЕБЕЗПЕКА",
            "AIR RAID ALERT — TYPE UNKNOWN": "ТРИВОГА · ТИП НЕВІДОМИЙ",
            "SAFE": "ВІДБІЙ",
            "UNKNOWN": "НЕВІДОМО",
        }.get(status, status)

    def render_status(self, unavailable_message=""):
        selected = self.region.currentText()
        chosen = [a for a in self.alerts if selected == "Вся Україна" or a.region == selected]
        if self.feed_unknown:
            status = "UNKNOWN"
            info = unavailable_message or "Немає актуальних даних. Безпечний стан не підтверджено."
        elif selected != "Вся Україна":
            status = next((a.classification for a in chosen), self.states.get(selected, "UNKNOWN"))
            info = (f"{chosen[0].region} · {chosen[0].started_at or 'Час початку відсутній'}" if chosen
                    else f"Для {selected} активних сповіщень не отримано")
        elif not self.alerts:
            status = "SAFE"
            info = "Активних сповіщень не отримано · це не є гарантією безпеки"
        else:
            rank = {"MISSILE / BOMBING DANGER": 3, "DRONE DANGER": 2, "AIR RAID ALERT — TYPE UNKNOWN": 1}
            status = max((a.classification for a in self.alerts), key=lambda s: rank.get(s, 0))
            info = f"{len(self.alerts)} регіон(ів) повідомляють про активні сповіщення"
        color = COLORS.get(status, COLORS["UNKNOWN"])
        self.status.setText(self._translate_status(status))
        self.status.setStyleSheet(f"color:{color}")
        self.hero_icon.setStyleSheet(f"color:{color};border:2px solid {color};border-radius:38px;font-size:30px")
        self.hero.setStyleSheet(f"QFrame#hero{{background:#101820;border:1px solid {color};border-radius:14px}}")
        self.alert_time.setText(info)

