import sys
from PySide6.QtWidgets import QApplication
from .config import DB_PATH
from .services.database import Database
from .services.secrets import get_api_token
from .ui.main_window import MainWindow

def main():
    simulation="--simulate" in sys.argv
    if simulation: sys.argv.remove("--simulate")
    app=QApplication(sys.argv); app.setQuitOnLastWindowClosed(False)
    db=Database(DB_PATH); window=MainWindow(db,get_api_token(),int(db.get("refresh_interval","30")),simulation); app.aboutToQuit.connect(window.shutdown); window.show()
    return app.exec()

if __name__=="__main__": raise SystemExit(main())
