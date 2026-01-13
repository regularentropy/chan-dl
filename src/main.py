from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QLineEdit,
    QFileDialog,
)
import subprocess
import platform
import os
import re

from models import DownloadThread, ProgressDialog, SuccessDialog
from helpers import show_error, show_warning, show_question


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chan-DL")
        self.setFixedWidth(440)
        self.setFixedHeight(200)

        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout()
        self.central_widget.setLayout(self.grid)

        self.entry_field = QLineEdit(placeholderText="Enter URL of thread here")
        self.folder_field = QLineEdit(placeholderText="Folder Path")
        self.folder_select = QPushButton("Select Folder")
        self.button = QPushButton("Download")

        self.folder_select.clicked.connect(self.set_folder)
        self.button.clicked.connect(self.start_downloading)

        self.grid.addWidget(self.entry_field, 0, 0, 1, -1)
        self.grid.addWidget(self.folder_field, 1, 0)
        self.grid.addWidget(self.folder_select, 1, 1)
        self.grid.addWidget(self.button, 2, 0, 1, -1)

    def set_folder(self):
        dialogue = QFileDialog().getExistingDirectory(self, "Select Folder", "")
        if dialogue:
            self.folder_field.setText(dialogue)

    def start_downloading(self):

        thread_link = self.entry_field.text()
        folder_path = self.folder_field.text()

        if not (self.entry_field.text()):
            show_error(self, "Thread link is not set")
            return

        if not (self.folder_field.text()):
            show_error(self, "Folder is not selected")
            return

        # Check if thread already exists locally
        match = re.search(r"boards\.4chan\.org/([^/]+)/thread/(\d+)", thread_link)
        if match:
            board = match.group(1)
            thread_id = match.group(2)
            thread_dir = os.path.join(folder_path, f"{board}_{thread_id}")

            if os.path.exists(thread_dir):
                if not show_question(
                    self,
                    "Folder Exists",
                    f"Thread folder '{board}_{thread_id}' already exists.\n\nDo you want to overwrite it?",
                ):
                    return

        # Create progress dialog
        progress_dialog = ProgressDialog(self)

        # Create download thread
        self.download_thread = DownloadThread(thread_link, folder_path)

        # Connect signals
        self.download_thread.progress_update.connect(progress_dialog.update_progress)
        self.download_thread.finished.connect(
            lambda success: self.download_finished(success, progress_dialog)
        )
        progress_dialog.cancel_button.clicked.connect(
            lambda: self.cancel_download(progress_dialog)
        )

        # Start the download
        self.download_thread.start()
        progress_dialog.exec()

    def cancel_download(self, dialog):
        if hasattr(self, "download_thread"):
            self.download_thread.cancel()
            dialog.accept()

    def open_folder(self, folder_path):
        """Open the folder in the system's file manager"""
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", folder_path])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            show_error(self, f"Could not open folder: {str(e)}")

    def download_finished(self, success, dialog):
        dialog.accept()
        if success:
            msg_box = SuccessDialog(self)
            msg_box.exec()

            if msg_box.was_open_folder_clicked():
                self.open_folder(self.download_thread.folder_path)
        else:
            show_warning(self, "Cancelled", "Download was cancelled")


app = QApplication()
window = MainWindow()
window.show()
app.exec()
