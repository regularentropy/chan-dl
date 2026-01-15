from PySide6.QtWidgets import QMessageBox


class SuccessDialog(QMessageBox):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Success")
		self.setText("Thread downloaded successfully!")
		self.setIcon(QMessageBox.Information)
		
		self.open_folder_button = self.addButton("Open Folder", QMessageBox.ActionRole)
		self.addButton(QMessageBox.Ok)
	
	def was_open_folder_clicked(self):
		"""Check if the 'Open Folder' button was clicked"""
		return self.clickedButton() == self.open_folder_button
