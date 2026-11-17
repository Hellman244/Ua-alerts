from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

class SoundService:
    def __init__(self, base: Path, enabled=True):
        self.effects = {}
        for kind in ("drone", "missile", "safe", "unknown"):
            path = base / "assets" / "sounds" / f"{kind}.wav"
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(str(path)))
            effect.setVolume(0.65)
            self.effects[kind] = effect
        self.enabled = enabled

    def play(self, kind):
        effect = self.effects.get(kind)
        if self.enabled and effect and effect.source().isValid(): effect.play()

    def set_volume(self, value):
        for effect in self.effects.values(): effect.setVolume(max(0, min(100, value)) / 100)
