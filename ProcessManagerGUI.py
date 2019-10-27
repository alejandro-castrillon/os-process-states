import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from process_manager import ProcessManager

class ProcessManagerGUI(Gtk.Window):
	def __init__(self):
		super().__init__(title="Process Manager")

		self.processManager = ProcessManager()

		self.show()
		self.connect("destroy", Gtk.main_quit)

	def load(self):
		pass

	def prepare_process(self):
		pass

	def execute_process(self):
		pass

	def deactivate_process(self):
		pass

	def suspend_process(self):
		pass


if __name__ == "__main__":
	processManagerGUI = ProcessManagerGUI()
	Gtk.main()