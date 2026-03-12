STYLE = """
QMainWindow { background: #f1f5f9; }
QWidget { color: #0f172a; font-size: 14px; }
#sidebar { background: #f8fafc; border-right: 1px solid #e2e8f0; }
#brandCard { background: #0f172a; border-radius: 22px; }
#brandTitle { color: white; font-size: 24px; font-weight: 700; }
#brandSub { color: #cbd5e1; font-size: 12px; }
#menu { background: transparent; border: none; }
#menu::item {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 4px 0;
    font-weight: 600;
}
#menu::item:selected {
    background: #0f172a;
    color: white;
    border: 1px solid #0f172a;
}
#card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
}
#pageTitle { font-size: 30px; font-weight: 700; }
#pageSub { color: #64748b; font-size: 13px; }
#statTitle { color: #64748b; font-size: 12px; }
#statValue { font-size: 28px; font-weight: 700; }
#statNote { color: #64748b; font-size: 12px; }
#primaryButton {
    background: #0f172a;
    color: white;
    border: 1px solid #0f172a;
    border-radius: 16px;
    padding: 11px 16px;
    font-weight: 700;
}
#dangerButton {
    background: #be123c;
    color: white;
    border: 1px solid #be123c;
    border-radius: 16px;
    padding: 11px 16px;
    font-weight: 700;
}
QPushButton {
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 11px 16px;
    font-weight: 700;
}
QPushButton:hover { background: #f8fafc; }
QTableWidget {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    gridline-color: #e2e8f0;
    alternate-background-color: #f8fafc;
}
QHeaderView::section {
    background: #f8fafc;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 10px;
    color: #475569;
    font-weight: 700;
}
QGraphicsView {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}
QGroupBox {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: 700;
}
"""
