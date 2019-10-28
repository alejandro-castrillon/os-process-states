import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from process_manager import ProcessManager


class ProcessManagerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Process Manager")
        self.connect("destroy", Gtk.main_quit)

        self.process_manager = ProcessManager()

        self.init_components()
        self.init_events()

    # def test(self, toggleButton):
    #     print(toggleButton.get_active())

    def init_components(self):
        inactive_processes = self.process_manager.inactive_processes

        grid = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)

        # Process Button
        self.add_process_button = Gtk.ToggleButton(label="Add Process")

        # Inactive Processes List
        self.inactive_processes_list_box = Gtk.ListBox()

        self.update_components()

        # Add Components
        grid.attach(
            child=self.inactive_processes_list_box, left=0, top=0, width=1, height=2
        )
        grid.attach(child=self.add_process_button, left=0, top=2, width=1, height=1)
        self.add(grid)
        # self.add(self.inactive_processes_list_box)

    def init_events(self):
        self.add_process_button.connect("clicked", self.add_process_action)

    def update_components(self):
        inactive_processes = self.process_manager.inactive_processes

        listChildren = self.inactive_processes_list_box.get_children()
        for i in listChildren:
            i.destroy()

        for i in inactive_processes:
            row = Gtk.ListBoxRow()
            box = Gtk.Box()

            process_button = Gtk.ToggleButton(label=i.name)
            process_button.connect("toggled", self.prepare_process_action)
            box.pack_start(process_button, True, True, 0)

            row.add(box)
            self.inactive_processes_list_box.add(row)

    def add_process_action(self, button):
        add_process_message_dialog = Gtk.MessageDialog(
            parent=self,
            title="Add New Process",
            text="Process Name:",
            buttons=Gtk.ButtonsType.OK_CANCEL,
        )

        process_name_entry = Gtk.Entry()
        process_name_entry.set_size_request(250, 0)
        add_process_message_dialog.get_content_area().pack_end(
            process_name_entry, False, False, 0
        )

        add_process_message_dialog.show_all()
        response = add_process_message_dialog.run()
        process_name = process_name_entry.get_text()
        add_process_message_dialog.destroy()

        if process_name and response == Gtk.ResponseType.OK:
            self.add_process(process_name)

    def add_process(self, process_name):
        self.process_manager.add_process(process_name)
        self.update_components()

    def prepare_process_action(self, button):
        self.prepare_process(button.get_label())
        print(button.get_label())
        print(button.get_active())

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
