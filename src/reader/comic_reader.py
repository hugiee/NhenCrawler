import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

BOOKMARK_FILE = "bookmarks.json"


def load_bookmarks():
    if os.path.exists(BOOKMARK_FILE):
        with open(BOOKMARK_FILE, "r") as f:
            return json.load(f)
    return {}


def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f)


class ReaderWindow(QWidget):
    def __init__(self, library_path):
        super().__init__()
        self.setWindowTitle("漫画阅读器")
        self.library_path = library_path
        self.bookmarks = load_bookmarks()
        self.current_manga = None
        self.current_index = 0
        self.image_files = []
        self.double_page = False

        # UI Components
        self.manga_list = QListWidget()
        self.thumbnail_list = QListWidget()
        self.image_label_left = QLabel()
        self.image_label_right = QLabel()
        self.btn_prev = QPushButton("上一页")
        self.btn_next = QPushButton("下一页")
        self.double_page_checkbox = QCheckBox("双页模式")

        self.setup_ui()
        self.load_manga_list()

        # Events
        self.manga_list.currentTextChanged.connect(self.load_manga)
        self.thumbnail_list.itemClicked.connect(self.select_thumbnail)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.double_page_checkbox.stateChanged.connect(self.toggle_double_page)

    def setup_ui(self):
        self.thumbnail_list.setIconSize(QSize(80, 100))
        self.thumbnail_list.setFixedWidth(100)

        self.image_label_left.setAlignment(Qt.AlignCenter)
        self.image_label_right.setAlignment(Qt.AlignCenter)

        img_layout = QHBoxLayout()
        img_layout.addWidget(self.image_label_left)
        img_layout.addWidget(self.image_label_right)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.double_page_checkbox)
        nav_layout.addWidget(self.btn_next)

        right_layout = QVBoxLayout()
        right_layout.addLayout(img_layout)
        right_layout.addLayout(nav_layout)

        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.manga_list)
        left_panel.addWidget(self.thumbnail_list)
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_layout, 4)

        self.setLayout(main_layout)

    def load_manga_list(self):
        for manga in sorted(os.listdir(self.library_path)):
            if os.path.isdir(os.path.join(self.library_path, manga)):
                self.manga_list.addItem(manga)

    def load_manga(self, manga_name):
        self.current_manga = manga_name
        folder = os.path.join(self.library_path, manga_name)
        self.image_files = sorted([
            f for f in os.listdir(folder)
            if f.lower().endswith(('.jpg', '.png'))
        ])
        self.current_index = self.bookmarks.get(manga_name, 0)
        self.load_thumbnails()
        self.update_image()

    def load_thumbnails(self):
        self.thumbnail_list.clear()
        folder = os.path.join(self.library_path, self.current_manga)
        for i, img_file in enumerate(self.image_files):
            path = os.path.join(folder, img_file)
            icon = QIcon(QPixmap(path).scaled(80, 100, Qt.KeepAspectRatio))
            item = QListWidgetItem(icon, str(i + 1))
            item.setData(Qt.UserRole, i)
            self.thumbnail_list.addItem(item)

    def select_thumbnail(self, item):
        self.current_index = item.data(Qt.UserRole)
        self.update_image()

    def update_image(self):
        if not self.current_manga or not self.image_files:
            return
        folder = os.path.join(self.library_path, self.current_manga)

        # First page
        left_path = os.path.join(folder, self.image_files[self.current_index])
        left_pixmap = QPixmap(left_path).scaled(800, 1000, Qt.KeepAspectRatio)
        self.image_label_left.setPixmap(left_pixmap)

        # Second page (if double page enabled and next page exists)
        if self.double_page and self.current_index + 1 < len(self.image_files):
            right_path = os.path.join(folder, self.image_files[self.current_index + 1])
            right_pixmap = QPixmap(right_path).scaled(800, 1000, Qt.KeepAspectRatio)
            self.image_label_right.setPixmap(right_pixmap)
        else:
            self.image_label_right.clear()

    def prev_page(self):
        step = 2 if self.double_page else 1
        if self.current_index - step >= 0:
            self.current_index -= step
            self.update_image()

    def next_page(self):
        step = 2 if self.double_page else 1
        if self.current_index + step < len(self.image_files):
            self.current_index += step
            self.update_image()

    def toggle_double_page(self, state):
        self.double_page = state == Qt.Checked
        self.update_image()

    def closeEvent(self, event):
        if self.current_manga:
            self.bookmarks[self.current_manga] = self.current_index
        save_bookmarks(self.bookmarks)
        event.accept()

def open_reader(library_path: str):
    import sys
    app = QApplication([])
    window = ReaderWindow(library_path)
    window.show()
    sys.exit(app.exec_())

