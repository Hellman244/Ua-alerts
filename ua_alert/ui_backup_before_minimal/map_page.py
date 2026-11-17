from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Signal
from ..config import REGIONS
from .map_widget import MapWidget, COLORS


class MapPage(QWidget):
    region_selected = Signal(str)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(14)
        title = QLabel("Карта областей")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Натисніть на область, щоб переглянути її поточний стан")
        subtitle.setObjectName("secondaryText")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        card = QFrame()
        card.setObjectName("statusPanel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        self.map = MapWidget(REGIONS)
        self.map.region_selected.connect(self.region_selected.emit)
        card_layout.addWidget(self.map, 1)
        legend = QHBoxLayout()
        for status, title_text in (("SAFE", "БЕЗ АКТИВНИХ ТРИВОГ"), ("DRONE DANGER", "ЗАГРОЗА БПЛА"),
                                   ("MISSILE / BOMBING DANGER", "РАКЕТНА / БОМБОВА"), ("UNKNOWN", "НЕВІДОМО")):
            item = QLabel(f"●  {title_text}")
            item.setStyleSheet(f"color:{COLORS[status]};font-size:10px;font-weight:750;padding:5px")
            legend.addWidget(item)
        legend.addStretch()
        card_layout.addLayout(legend)
        layout.addWidget(card, 1)

    def set_states(self, states):
        self.map.update_states(states)
