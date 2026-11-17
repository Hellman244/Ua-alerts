from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

COLORS = {
    "SAFE": "#35B77A",
    "DRONE DANGER": "#D7AB31",
    "MISSILE / BOMBING DANGER": "#E64F4A",
    "AIR RAID ALERT — TYPE UNKNOWN": "#788594",
    "UNKNOWN": "#788594",
}

# Approximate tile placement keeps the overview readable and suggestive of the
# country's outline while avoiding a misleading claim of exact boundaries.
TILE_POSITIONS = {
    "Автономна Республіка Крим": (6, 4), "Волинська область": (0, 2),
    "Вінницька область": (3, 3), "Дніпропетровська область": (3, 5),
    "Донецька область": (3, 7), "Житомирська область": (1, 3),
    "Закарпатська область": (3, 0), "Запорізька область": (4, 6),
    "Івано-Франківська область": (3, 1), "Київська область": (1, 4),
    "Кіровоградська область": (3, 4), "Луганська область": (2, 7),
    "Львівська область": (2, 0), "Миколаївська область": (4, 4),
    "Одеська область": (4, 3), "Полтавська область": (2, 5),
    "Рівненська область": (1, 2), "Сумська область": (1, 6),
    "Тернопільська область": (2, 2), "Харківська область": (2, 6),
    "Херсонська область": (5, 4), "Хмельницька область": (2, 3),
    "Черкаська область": (2, 4), "Чернівецька область": (4, 1),
    "Чернігівська область": (0, 5), "м. Київ": (1, 5),
}


class MapWidget(QWidget):
    region_selected = Signal(str)

    def __init__(self, regions):
        super().__init__()
        self.regions = regions
        self.states = {}
        self.buttons = {}
        grid = QGridLayout(self)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        for _, uk, _en in regions:
            label = uk.replace(" область", "").replace("Автономна Республіка Крим", "АР Крим").replace("м. Київ", "Київ")
            button = QPushButton(label)
            button.setMinimumSize(72, 48)
            button.setMaximumWidth(104)
            button.setToolTip(uk)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, title=uk: self.region_selected.emit(title))
            self.buttons[uk] = button
            row, col = TILE_POSITIONS.get(uk, (0, 0))
            grid.addWidget(button, row, col)
        self.update_states({})

    def update_states(self, states):
        self.states = states
        for _, region, _ in self.regions:
            status = states.get(region, "UNKNOWN")
            color = COLORS.get(status, COLORS["UNKNOWN"])
            red, green, blue, _ = QColor(color).getRgb()
            tint = f"rgba({red},{green},{blue},24)"
            border = f"rgba({red},{green},{blue},110)"
            hover = f"rgba({red},{green},{blue},58)"
            solid = f"rgb({red},{green},{blue})"
            button = self.buttons[region]
            button.setStyleSheet(
                "QPushButton{"
                f"background:{tint};color:#dbe2e9;border:1px solid {border};"
                "border-radius:9px;padding:5px 4px;font-size:9px;font-weight:600;"
                "} QPushButton:hover{"
                f"background:{hover};border:1px solid {solid};color:#fff;"
                "} QPushButton:pressed{"
                f"background:rgba({red},{green},{blue},90);"
                "}"
            )
