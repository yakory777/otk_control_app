STYLE = """
/* ── Базовые ── */
QMainWindow, QDialog {
    background: #f1f5f9;
}
QWidget {
    color: #0f172a;
    font-size: 14px;
    font-family: "Segoe UI", sans-serif;
}

/* ── Сайдбар ── */
#sidebar { background: #f8fafc; border-right: 1px solid #e2e8f0; }
#brandCard { background: #0f172a; border-radius: 22px; }
#brandTitle { color: white; font-size: 24px; font-weight: 700; }
#brandSub   { color: #cbd5e1; font-size: 12px; }

/* ── Меню сайдбара ── */
#menu { background: transparent; border: none; }
#menu::item {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 4px 0;
    font-weight: 600;
    color: #0f172a;
}
#menu::item:selected {
    background: #0f172a;
    color: white;
    border: 1px solid #0f172a;
}
#menu::item:hover:!selected { background: #f1f5f9; }

/* ── Карточки ── */
#card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
}

/* ── Заголовки страниц ── */
#pageTitle { font-size: 30px; font-weight: 700; color: #0f172a; }
#pageSub   { color: #64748b; font-size: 13px; }
#statTitle { color: #64748b; font-size: 12px; }
#statValue { font-size: 28px; font-weight: 700; color: #0f172a; }
#statNote  { color: #64748b; font-size: 12px; }

/* ── Кнопки ── */
QPushButton {
    background: white;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 11px 16px;
    font-weight: 700;
}
QPushButton:hover    { background: #f1f5f9; }
QPushButton:pressed  { background: #e2e8f0; }
QPushButton:disabled { background: #f8fafc; color: #94a3b8; }

#primaryButton {
    background: #0f172a;
    color: white;
    border: 1px solid #0f172a;
    border-radius: 16px;
    padding: 11px 16px;
    font-weight: 700;
}
#primaryButton:hover { background: #1e293b; }

#dangerButton {
    background: #be123c;
    color: white;
    border: 1px solid #be123c;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}
#dangerButton:hover { background: #9f1239; }

/* ── Поля ввода ── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: white;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 12px;
    selection-background-color: #0f172a;
    selection-color: white;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #0f172a;
}
QLineEdit:disabled { background: #f8fafc; color: #94a3b8; }

/* ── Выпадающий список ── */
QComboBox {
    background: white;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 12px;
}
QComboBox:focus { border: 1px solid #0f172a; }
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: white;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
    outline: none;
}

/* ── Таблица ── */
QTableWidget {
    background: white;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    gridline-color: #e2e8f0;
    alternate-background-color: #f8fafc;
}
QTableWidget::item { color: #0f172a; padding: 4px 6px; }
QTableWidget::item:selected {
    background: #0f172a;
    color: white;
}
QHeaderView::section {
    background: #f8fafc;
    color: #475569;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 10px;
    font-weight: 700;
}

/* ── Полосы прокрутки ── */
QScrollBar:vertical {
    background: #f8fafc;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #f8fafc;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #94a3b8; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Группы и viewer ── */
QGroupBox {
    background: white;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    margin-top: 8px;
    padding-top: 12px;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    color: #0f172a;
}

QGraphicsView {
    background: #1e2030;
    border: 1px solid #334155;
    border-radius: 16px;
}

/* ── Диалоги ── */
QDialogButtonBox QPushButton { min-width: 80px; }

/* ── Form layout labels ── */
QLabel { color: #0f172a; background: transparent; }

/* ── Карточки контрольных точек ── */
#pointCard {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}
#pointCard:hover {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
}
#pointCardSelected {
    background: #0f172a;
    border: 1px solid #0f172a;
    border-radius: 16px;
    color: white;
}
#pointCardSelected QLabel { color: white; }

/* ── Ячейки свойств выбранного размера ── */
#propCell {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}
"""
