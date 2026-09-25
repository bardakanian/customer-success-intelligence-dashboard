"""Centralized light and dark themes for the desktop application."""

LIGHT = """
QWidget { background:#F4F6F9; color:#182230; font-size:13px; }
QMainWindow, QDialog { background:#F4F6F9; }
QLabel { background:transparent; }
QFrame#sidebar { background:#122033; border:none; }
QFrame#sidebar QLabel { color:#F8FAFC; background:transparent; }
QLabel#navSection { color:#73839A; font-size:10px; font-weight:700; letter-spacing:1px; padding:8px 10px 4px 10px; }
QPushButton#nav { background:transparent; color:#AAB7C9; border:none; border-radius:7px; text-align:left; padding:10px 14px; font-weight:600; }
QPushButton#nav:hover { background:#1C3049; color:#FFFFFF; }
QPushButton#nav:pressed { background:#263B56; }
QPushButton#nav:checked { background:#2865CB; color:#FFFFFF; }
QFrame#header { background:#FAFBFC; border-bottom:1px solid #DEE4EC; }
QFrame.card, QFrame#card, QFrame#toolbar { background:#FFFFFF; border:1px solid #E0E6ED; border-radius:10px; }
QFrame#subtlePanel { background:#F8FAFC; border:1px solid #E7EBF1; border-radius:8px; }
QLabel#title { font-size:23px; font-weight:700; color:#142033; }
QLabel#headerTitle { font-size:15px; font-weight:700; color:#26354A; }
QLabel#subtitle { color:#66758B; font-size:12px; }
QLabel#metric { font-size:24px; font-weight:700; color:#172033; }
QLabel#metricLabel { color:#6A788D; font-size:11px; font-weight:700; letter-spacing:.3px; }
QLabel#section { font-size:16px; font-weight:700; color:#1B2738; }
QLabel#eyebrow { color:#77869B; font-size:10px; font-weight:700; letter-spacing:.7px; }
QLineEdit, QComboBox, QTextEdit, QDateEdit { background:#FFFFFF; color:#1D2939; border:1px solid #CFD7E3; border-radius:7px; padding:7px 9px; selection-background-color:#2D6CDF; min-height:20px; }
QLineEdit:hover, QComboBox:hover, QTextEdit:hover { border-color:#AAB6C6; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus { border:1px solid #2D6CDF; }
QComboBox::drop-down { border:none; width:24px; }
QComboBox QAbstractItemView { background:#FFFFFF; color:#1D2939; border:1px solid #D4DCE7; selection-background-color:#E8F0FD; selection-color:#172033; padding:4px; }
QPushButton { min-height:20px; }
QPushButton#primary { background:#2867D4; color:white; border:1px solid #2867D4; padding:8px 14px; border-radius:7px; font-weight:700; }
QPushButton#primary:hover { background:#205ABF; border-color:#205ABF; }
QPushButton#primary:pressed { background:#194B9F; }
QPushButton#primary:disabled { background:#A9BDD9; border-color:#A9BDD9; color:#EDF2F8; }
QPushButton#secondary, QPushButton#segment { background:#FFFFFF; color:#334155; border:1px solid #D3DAE4; padding:7px 12px; border-radius:7px; font-weight:600; }
QPushButton#secondary:hover, QPushButton#segment:hover { background:#F5F8FC; border-color:#AEB9C8; }
QPushButton#secondary:pressed, QPushButton#segment:pressed { background:#E9EEF5; }
QPushButton#segment:checked { background:#E8F0FD; color:#1E5AB8; border-color:#7FA5E3; }
QPushButton#textButton { background:transparent; color:#2867D4; border:none; padding:6px 8px; font-weight:600; }
QPushButton#textButton:hover { background:#EDF3FC; border-radius:6px; }
QTableWidget { background:#FFFFFF; alternate-background-color:#FAFBFD; border:1px solid #E0E6ED; border-radius:8px; gridline-color:transparent; selection-background-color:#E7F0FE; selection-color:#172033; outline:0; }
QTableWidget::item { padding:7px 9px; border-bottom:1px solid #EDF0F4; }
QTableWidget::item:hover { background:#F0F5FC; }
QHeaderView::section { background:#F5F7FA; color:#5D6B80; border:none; border-bottom:1px solid #DDE3EB; padding:9px 8px; font-size:11px; font-weight:700; }
QHeaderView::section:hover { background:#EDF1F6; }
QProgressBar { background:#E7ECF2; border:none; border-radius:4px; }
QProgressBar::chunk { background:#3D78D8; border-radius:4px; }
QTabWidget::pane { background:#FFFFFF; border:1px solid #DDE3EB; border-radius:8px; top:-1px; }
QTabBar::tab { background:#EEF2F6; color:#5F6D81; border:1px solid #DDE3EB; padding:9px 16px; font-weight:600; }
QTabBar::tab:selected { background:#FFFFFF; color:#1F4F99; border-bottom-color:#FFFFFF; }
QTabBar::tab:hover:!selected { background:#E6EBF2; }
QCheckBox { spacing:7px; color:#465468; }
QCheckBox::indicator { width:16px; height:16px; }
QScrollArea { border:none; background:transparent; }
QScrollBar:vertical { background:transparent; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:#C4CDD9; border-radius:5px; min-height:35px; }
QScrollBar::handle:vertical:hover { background:#AEB9C7; }
QScrollBar:horizontal { background:transparent; height:9px; }
QScrollBar::handle:horizontal { background:#C4CDD9; border-radius:4px; min-width:40px; }
QStatusBar { background:#FAFBFC; color:#5D6B80; border-top:1px solid #E1E6ED; font-size:11px; }
QToolTip { background:#172033; color:white; border:1px solid #172033; border-radius:4px; padding:6px; }
QDialogButtonBox QPushButton { min-width:78px; padding:7px 12px; }
"""

DARK = """
QWidget { background:#101722; color:#E7ECF3; font-size:13px; }
QMainWindow, QDialog { background:#101722; }
QLabel { background:transparent; }
QFrame#sidebar { background:#0A111C; border:none; }
QFrame#sidebar QLabel { color:#F6F8FB; background:transparent; }
QLabel#navSection { color:#66768E; font-size:10px; font-weight:700; letter-spacing:1px; padding:8px 10px 4px 10px; }
QPushButton#nav { background:transparent; color:#8FA0B8; border:none; border-radius:7px; text-align:left; padding:10px 14px; font-weight:600; }
QPushButton#nav:hover { background:#18263A; color:#FFFFFF; }
QPushButton#nav:pressed { background:#22334B; }
QPushButton#nav:checked { background:#2E67C7; color:#FFFFFF; }
QFrame#header { background:#141E2C; border-bottom:1px solid #293548; }
QFrame.card, QFrame#card, QFrame#toolbar { background:#172130; border:1px solid #2A374A; border-radius:10px; }
QFrame#subtlePanel { background:#131C29; border:1px solid #273448; border-radius:8px; }
QLabel#title { font-size:23px; font-weight:700; color:#F4F7FB; }
QLabel#headerTitle { font-size:15px; font-weight:700; color:#E9EEF5; }
QLabel#subtitle { color:#96A4B8; font-size:12px; }
QLabel#metric { font-size:24px; font-weight:700; color:#F4F7FB; }
QLabel#metricLabel { color:#96A4B8; font-size:11px; font-weight:700; letter-spacing:.3px; }
QLabel#section { font-size:16px; font-weight:700; color:#EEF2F7; }
QLabel#eyebrow { color:#8291A7; font-size:10px; font-weight:700; letter-spacing:.7px; }
QLineEdit, QComboBox, QTextEdit, QDateEdit { background:#0F1825; color:#E7ECF3; border:1px solid #354358; border-radius:7px; padding:7px 9px; selection-background-color:#346BC5; min-height:20px; }
QLineEdit:hover, QComboBox:hover, QTextEdit:hover { border-color:#526078; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus { border:1px solid #4B83DD; }
QComboBox::drop-down { border:none; width:24px; }
QComboBox QAbstractItemView { background:#172130; color:#E7ECF3; border:1px solid #354358; selection-background-color:#294A78; padding:4px; }
QPushButton { min-height:20px; }
QPushButton#primary { background:#356FCF; color:white; border:1px solid #356FCF; padding:8px 14px; border-radius:7px; font-weight:700; }
QPushButton#primary:hover { background:#417DDB; }
QPushButton#primary:pressed { background:#2B5EAF; }
QPushButton#primary:disabled { background:#33445D; border-color:#33445D; color:#79879A; }
QPushButton#secondary, QPushButton#segment { background:#172130; color:#DCE3EC; border:1px solid #3A485C; padding:7px 12px; border-radius:7px; font-weight:600; }
QPushButton#secondary:hover, QPushButton#segment:hover { background:#202D3F; border-color:#526078; }
QPushButton#secondary:pressed, QPushButton#segment:pressed { background:#29374B; }
QPushButton#segment:checked { background:#223C63; color:#9FC3FC; border-color:#4A78BE; }
QPushButton#textButton { background:transparent; color:#7CACF4; border:none; padding:6px 8px; font-weight:600; }
QPushButton#textButton:hover { background:#1B2A40; border-radius:6px; }
QTableWidget { background:#172130; alternate-background-color:#192536; color:#E5EAF2; border:1px solid #2A374A; border-radius:8px; gridline-color:transparent; selection-background-color:#274875; selection-color:#FFFFFF; outline:0; }
QTableWidget::item { padding:7px 9px; border-bottom:1px solid #273448; }
QTableWidget::item:hover { background:#202E42; }
QHeaderView::section { background:#1D293A; color:#A7B3C5; border:none; border-bottom:1px solid #354358; padding:9px 8px; font-size:11px; font-weight:700; }
QHeaderView::section:hover { background:#253348; }
QProgressBar { background:#263346; border:none; border-radius:4px; }
QProgressBar::chunk { background:#4A86E2; border-radius:4px; }
QTabWidget::pane { background:#172130; border:1px solid #2D3A4D; border-radius:8px; top:-1px; }
QTabBar::tab { background:#131C29; color:#91A0B5; border:1px solid #2D3A4D; padding:9px 16px; font-weight:600; }
QTabBar::tab:selected { background:#172130; color:#B8D2FB; border-bottom-color:#172130; }
QTabBar::tab:hover:!selected { background:#202C3D; }
QCheckBox { spacing:7px; color:#AAB6C8; }
QCheckBox::indicator { width:16px; height:16px; }
QScrollArea { border:none; background:transparent; }
QScrollBar:vertical { background:transparent; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:#46556B; border-radius:5px; min-height:35px; }
QScrollBar::handle:vertical:hover { background:#5A6A82; }
QScrollBar:horizontal { background:transparent; height:9px; }
QScrollBar::handle:horizontal { background:#46556B; border-radius:4px; min-width:40px; }
QStatusBar { background:#141E2C; color:#91A0B5; border-top:1px solid #293548; font-size:11px; }
QToolTip { background:#EDF2F7; color:#172033; border:1px solid #C8D1DD; border-radius:4px; padding:6px; }
QDialogButtonBox QPushButton { min-width:78px; padding:7px 12px; }
"""
