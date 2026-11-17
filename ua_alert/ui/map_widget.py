import json
import math
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QFontMetrics

COLORS = {
    "SAFE": "#4caf82",
    "DRONE DANGER": "#d1a63a",
    "MISSILE / BOMBING DANGER": "#e5534b",
    "AIR RAID ALERT — TYPE UNKNOWN": "#6b6b72",
    "UNKNOWN": "#6b6b72",
}

STATUS_TITLES = {
    "SAFE": "без активних тривог",
    "DRONE DANGER": "загроза БпЛА",
    "MISSILE / BOMBING DANGER": "ракетна / бомбова небезпека",
    "AIR RAID ALERT — TYPE UNKNOWN": "тривога · тип невідомий",
    "UNKNOWN": "невідомо",
}

DATA_FILE = Path(__file__).resolve().parents[1] / "assets" / "ukraine_regions.json"
KYIV_CITY = "м. Київ"
SEVASTOPOL = "м. Севастополь"  # drawn for geographic completeness; not one of the app's alert regions
NO_LABEL = {KYIV_CITY, SEVASTOPOL}


def _short(name):
    return name.replace(" область", "").replace("Автономна Республіка Крим", "АР Крим")


def _load_geometry():
    """Region outlines (OpenStreetMap, ODbL) as {name: [ring, ...]} with lon/lat points."""
    with open(DATA_FILE, encoding="utf-8") as handle:
        return json.load(handle)


class MapWidget(QWidget):
    """Geographic map of Ukraine's oblasts. Click an oblast to select it."""
    region_selected = Signal(str)

    def __init__(self, regions):
        super().__init__()
        self.regions = regions
        self.states = {}
        self.hovered = None
        self.setMouseTracking(True)
        self.setMinimumSize(420, 280)
        # Equirectangular projection corrected for latitude keeps the country's familiar shape.
        k = math.cos(math.radians(48.5))
        self.projected = {
            name: [[(lon * k, -lat) for lon, lat in ring] for ring in rings]
            for name, rings in _load_geometry().items()
        }
        xs = [x for rings in self.projected.values() for ring in rings for x, _ in ring]
        ys = [y for rings in self.projected.values() for ring in rings for _, y in ring]
        self.bounds = QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        # Kyiv city is drawn last so that it stays visible and clickable on top of Kyiv Oblast.
        self.order = [n for n in self.projected if n not in (KYIV_CITY, SEVASTOPOL)] + [KYIV_CITY]
        self.paths = {}
        self.label_points = {}

    def _rebuild_paths(self):
        margin = 14
        w, h = max(self.width() - 2 * margin, 10), max(self.height() - 2 * margin, 10)
        scale = min(w / self.bounds.width(), h / self.bounds.height())
        ox = margin + (w - self.bounds.width() * scale) / 2
        oy = margin + (h - self.bounds.height() * scale) / 2
        self.paths, self.label_points = {}, {}
        for name, rings in self.projected.items():
            path = QPainterPath()
            best_area, best_center = -1, None
            for ring in rings:
                pts = [QPointF(ox + (x - self.bounds.left()) * scale, oy + (y - self.bounds.top()) * scale)
                       for x, y in ring]
                ring_path = QPainterPath()
                ring_path.moveTo(pts[0])
                for p in pts[1:]:
                    ring_path.lineTo(p)
                ring_path.closeSubpath()
                path.addPath(ring_path)
                rect = ring_path.boundingRect()
                if rect.width() * rect.height() > best_area:
                    best_area = rect.width() * rect.height()
                    best_center = self._centroid(pts)
            self.paths[name] = path
            self.label_points[name] = best_center

    @staticmethod
    def _centroid(pts):
        area = cx = cy = 0.0
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            cross = p.x() * q.y() - q.x() * p.y()
            area += cross
            cx += (p.x() + q.x()) * cross
            cy += (p.y() + q.y()) * cross
        if abs(area) < 1e-6:
            return pts[0]
        return QPointF(cx / (3 * area), cy / (3 * area))

    def resizeEvent(self, event):
        self._rebuild_paths()
        super().resizeEvent(event)

    def update_states(self, states):
        self.states = states
        self.update()

    def _color(self, name):
        return QColor(COLORS.get(self.states.get(name, "UNKNOWN"), COLORS["UNKNOWN"]))

    def paintEvent(self, event):
        if not self.paths:
            self._rebuild_paths()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#2a2a2f"), 1))
        painter.setBrush(QColor(255, 255, 255, 8))
        painter.drawPath(self.paths[SEVASTOPOL])
        for name in self.order:
            fill = self._color(name)
            fill.setAlpha(150 if name == KYIV_CITY else (96 if name == self.hovered else 50))
            painter.setBrush(QBrush(fill))
            painter.setPen(QPen(QColor(255, 255, 255, 70), 0.8))
            painter.drawPath(self.paths[name])
        if self.hovered:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#e8e8ea"), 1.5))
            painter.drawPath(self.paths[self.hovered])
        self._paint_labels(painter)
        self._paint_caption(painter)

    def _paint_labels(self, painter):
        font = QFont(self.font())
        font.setPixelSize(10 if self.width() > 700 else 9)
        painter.setFont(font)
        painter.setPen(QColor("#d0d0d5"))
        metrics = QFontMetrics(font)
        for _, name, _ in self.regions:
            if name in NO_LABEL or name not in self.label_points:
                continue
            text = _short(name)
            center = self.label_points[name]
            text_w = metrics.horizontalAdvance(text)
            if text_w > self.paths[name].boundingRect().width() * 1.05:
                continue  # skip labels that would spill over a small oblast
            painter.drawText(QRectF(center.x() - text_w / 2 - 2, center.y() - 8, text_w + 4, 16),
                             Qt.AlignmentFlag.AlignCenter, text)

    def _paint_caption(self, painter):
        if not self.hovered:
            return
        name = self.hovered
        status = STATUS_TITLES.get(self.states.get(name, "UNKNOWN"), "невідомо")
        font = QFont(self.font())
        font.setPixelSize(12)
        painter.setFont(font)
        painter.setPen(self._color(name))
        painter.drawText(QPointF(16, 24), "●")
        painter.setPen(QColor("#e8e8ea"))
        painter.drawText(QPointF(32, 24), name)
        painter.setPen(QColor("#8a8a90"))
        painter.drawText(QPointF(32, 42), status)

    def _region_at(self, point):
        for name in reversed(self.order):
            if self.paths[name].contains(point):
                return name
        return None

    def mouseMoveEvent(self, event):
        name = self._region_at(event.position())
        if name != self.hovered:
            self.hovered = name
            self.setCursor(Qt.CursorShape.PointingHandCursor if name else Qt.CursorShape.ArrowCursor)
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.hovered:
            self.hovered = None
            self.unsetCursor()
            self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            name = self._region_at(event.position())
            if name:
                self.region_selected.emit(name)
        super().mouseReleaseEvent(event)
