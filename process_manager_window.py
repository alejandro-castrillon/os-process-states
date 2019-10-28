import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from process_manager import ProcessManager


class ProcessManagerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Process Manager")
        self.connect("destroy", Gtk.main_quit)

        self.processManager = ProcessManager()
        self.init_components()
        self.init_events()

    def init_components(self):
        inactive_processes = self.processManager.inactive_processes

        grid = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)

        # Process Button
        self.addProcessButton = Gtk.Button(label="Add Process")

        # Inactive Processes List
        self.inactiveListsListBox = Gtk.ListBox()

        for i in inactive_processes:
            row = Gtk.ListBoxRow()
            box = Gtk.Box()

            process_button = Gtk.Button(label=i.name)
            process_button.connect("clicked", self.prepare_process_action)
            box.pack_start(process_button, True, True, 0)

            row.add(box)
            self.inactiveListsListBox.add(row)

        # Add Components
        self.add(self.addProcessButton)
        # self.add(self.inactiveListsListBox)

    def init_events(self):
        self.addProcessButton.connect("clicked", self.add_process_action)

    def update_components(self):
        pass

    def add_process_action(self, button):
        print(button.get_label())

    def add_process(self, process_name):
        self.processManager.add_process(process_name)
        self.update_components()

    def prepare_process_action(self, button):
        self.prepare_process(button.get_label())

    def prepare_process(self, process_name):
        pass

    def execute_process_action(self, button):
        pass

    def execute_process(self, process_pid):
        pass

    def deactivate_process_action(self, button):
        pass

    def deactivate_process(self, proces_pid):
        pass

    def suspend_process_action(self, button):
        pass

    def suspend_process(self, process_pid):
        pass


if __name__ == "__main__":
    ProcessManagerWindow().show_all()
    Gtk.main()
