from PySide6.QtCore import QThread, Signal

from downloader import download_4chan_thread


class DownloadThread(QThread):
	progress_update = Signal(int, int, int, str)  # current_file, total_files, bytes_downloaded, filename
	finished = Signal(bool)  # success
	
	def __init__(self, thread_url, folder_path):
		super().__init__()
		self.thread_url = thread_url
		self.folder_path = folder_path
		self.cancelled = False
	
	def run(self):
		def progress_callback(current, total, bytes_downloaded, filename):
			self.progress_update.emit(current, total, bytes_downloaded, filename)
		
		def cancel_check():
			return self.cancelled
		
		success = download_4chan_thread(
			self.thread_url, 
			self.folder_path, 
			progress_callback=progress_callback,
			cancel_check=cancel_check
		)
		self.finished.emit(success)
	
	def cancel(self):
		self.cancelled = True
