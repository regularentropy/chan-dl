from PySide6.QtWidgets import QMessageBox


def show_error(parent, message):
	"""Show an error message box"""
	QMessageBox.warning(parent, "Error", message)


def show_warning(parent, title, message):
	"""Show a warning message box"""
	QMessageBox.warning(parent, title, message)


def show_question(parent, title, message, default_no=True):
	"""Show a question dialog and return True if Yes was clicked"""
	default_button = QMessageBox.No if default_no else QMessageBox.Yes
	reply = QMessageBox.question(
		parent,
		title,
		message,
		QMessageBox.Yes | QMessageBox.No,
		default_button
	)
	return reply == QMessageBox.Yes
