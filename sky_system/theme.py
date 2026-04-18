APP_STYLE = """
QWidget {
    background: #f7fbff;
    color: #1f2d3d;
    font-size: 14px;
    font-family: Microsoft YaHei;
}

QMainWindow {
    background: #f7fbff;
}

#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff,
                                stop:0.5 #f7fbff,
                                stop:1 #edf6ff);
    border-right: 1px solid #dce9f6;
}

#SidebarTitle {
    font-size: 24px;
    font-weight: 800;
    color: #2a8cff;
    padding: 14px 10px;
}

#PageTitle {
    font-size: 25px;
    font-weight: 800;
    color: #123b63;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #ffffff,
                                stop:1 #f3f9ff);
    border: 1px solid #d7e8f8;
    border-radius: 18px;
    padding: 12px 16px;
    color: #234;
    font-weight: 600;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #ffffff,
                                stop:1 #eaf5ff);
    border: 1px solid #bcdcff;
}

QPushButton:pressed {
    background: #dceeff;
}

#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #5db1ff,
                                stop:0.5 #2f95ff,
                                stop:1 #1677d8);
    color: white;
    border: none;
    border-radius: 20px;
    padding: 13px 18px;
    font-weight: 800;
}

#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #78beff,
                                stop:0.5 #47a2ff,
                                stop:1 #1c84ea);
}

QLineEdit, QTextEdit, QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #ffffff,
                                stop:1 #f8fbff);
    border: 1px solid #d2e3f2;
    border-radius: 18px;
    padding: 10px 12px;
    selection-background-color: #b9ddff;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #8dc7ff;
    background: #ffffff;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #dbe8f4;
    border-radius: 20px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    border-radius: 14px;
    padding: 8px;
    margin: 4px 2px;
}

QListWidget::item:selected {
    background: #e7f3ff;
    color: #123b63;
}

QFrame#Card {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #ffffff,
                                stop:0.55 #fbfdff,
                                stop:1 #f4faff);
    border: 1px solid #deebf7;
    border-radius: 26px;
}

QLabel#Muted {
    color: #6d8298;
}

QLabel#BigValue {
    font-size: 32px;
    font-weight: 900;
    color: #2387f3;
}

QLabel#TagLabel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #eef7ff,
                                stop:1 #dff0ff);
    color: #145b96;
    border: 1px solid #cfe6fb;
    border-radius: 14px;
    padding: 6px 12px;
    font-weight: 700;
}

QScrollArea {
    border: none;
    background: transparent;
}

QTextBrowser {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #f5faff,
                                stop:1 #edf6ff);
    border: 1px solid #d9e7f4;
    border-radius: 24px;
    padding: 14px;
}

QStackedWidget {
    background: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 6px 2px 6px 2px;
}

QScrollBar::handle:vertical {
    background: #cfe6fb;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #b7d9f7;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0px;
}
"""