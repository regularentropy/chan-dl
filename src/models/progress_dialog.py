from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton


class ProgressDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Downloading...")
		self.setFixedWidth(400)
		self.setFixedHeight(150)
		
		layout = QVBoxLayout()
		
		self.status_label = QLabel("Starting download...")
		self.progress_bar = QProgressBar()
		self.size_label = QLabel("Downloaded: 0.00 MB")
		self.cancel_button = QPushButton("Cancel")
		
		layout.addWidget(self.status_label)
		layout.addWidget(self.progress_bar)
		layout.addWidget(self.size_label)
		layout.addWidget(self.cancel_button)
		
		self.setLayout(layout)
		
	def update_progress(self, current, total, bytes_downloaded, filename):
		self.progress_bar.setMaximum(total)
		self.progress_bar.setValue(current)
		mb_downloaded = bytes_downloaded / (1024 * 1024)
		self.status_label.setText(f"Downloading: {filename}")
		self.size_label.setText(f"Downloaded: {mb_downloaded:.2f} MB ({current}/{total} files)")
