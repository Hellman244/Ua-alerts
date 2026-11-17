from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QHBoxLayout, QLabel
import csv

class HistoryPage(QWidget):
    def __init__(self, database):
        super().__init__(); self.db=database; layout=QVBoxLayout(self); layout.setContentsMargins(28,24,28,20); layout.setSpacing(16)
        title=QLabel("Історія сповіщень"); title.setObjectName("pageTitle"); layout.addWidget(title)
        row=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Пошук регіону або категорії…"); self.search.textChanged.connect(self.refresh)
        export=QPushButton("Експортувати CSV"); export.clicked.connect(self.export_csv); row.addWidget(self.search); row.addWidget(export); layout.addLayout(row)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["Час","Регіон","Попередній стан","Новий стан","Категорія загрози"]); self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table); self.refresh()
    def refresh(self):
        rows=self.db.history(self.search.text()); self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            fields=("created_at","region","previous_status","new_status","threat_category")
            for c,k in enumerate(fields):
                value=str(row[k] or "")
                value={"DRONE DANGER":"ЗАГРОЗА БПЛА","MISSILE / BOMBING DANGER":"РАКЕТНА / БОМБОВА НЕБЕЗПЕКА",
                       "AIR RAID ALERT — TYPE UNKNOWN":"ТРИВОГА · ТИП НЕВІДОМИЙ","SAFE":"ВІДБІЙ","UNKNOWN":"НЕВІДОМО"}.get(value,value)
                self.table.setItem(r,c,QTableWidgetItem(value))
    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,"Експорт історії","ua-alert-history.csv","CSV (*.csv)")
        if path:
            rows=self.db.history(self.search.text())
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.writer(f); w.writerow(rows[0].keys() if rows else ["id","event_key","region","previous_status","new_status","threat_category","started_at","ended_at","source","created_at"]); w.writerows([tuple(r) for r in rows])
