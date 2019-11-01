import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from process_manager import ProcessManager


class ProcessManagerWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Process Manager")
        self.connect("destroy", Gtk.main_quit)
        # self.set_size_request(300, 300)

        self.executing = False
        self.process_manager = ProcessManager()

        self.init_components()
        self.init_events()

    def init_components(self):
        inactive_processes = self.process_manager.inactive_processes

        grid = Gtk.Grid(
            row_homogeneous=True,
            column_homogeneous=True,
            row_spacing=5,
            column_spacing=5,
        )

        # Process Button -------------------------------------------------------
        self.add_process_button = Gtk.Button(label="Add Process")

        # Inactive Processes List ----------------------------------------------
        self.inactive_processes_list_box = Gtk.ListBox()
        self.inactive_processes_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        inactive_processes_scrolled_window = Gtk.ScrolledWindow()
        inactive_processes_scrolled_window.add(self.inactive_processes_list_box)

        # Inactive Processes List ----------------------------------------------
        self.prepared_processes_list_box = Gtk.ListBox()
        prepared_processes_scrolled_window = Gtk.ScrolledWindow()
        prepared_processes_scrolled_window.add(self.prepared_processes_list_box)

        # Inactive Processes List ----------------------------------------------
        self.executed_process_label = Gtk.Label()
        self.executed_process_label.set_halign(Gtk.Align.CENTER)

        # Inactive Processes List ----------------------------------------------
        self.suspended_processes_list_box = Gtk.ListBox()
        suspended_processes_scrolled_window = Gtk.ScrolledWindow()
        suspended_processes_scrolled_window.add(self.suspended_processes_list_box)

        self.update_components()

        # Add Components -------------------------------------------------------
        grid.attach(Gtk.Label(label="Inactive Processes"), 0, 0, 1, 1)
        grid.attach(inactive_processes_scrolled_window, 0, 1, 1, 18)
        grid.attach(self.add_process_button, 0, 19, 1, 1)
        grid.attach(Gtk.Label(label="Prepared Processes"), 1, 0, 5, 1)
        grid.attach(prepared_processes_scrolled_window, 1, 1, 5, 19)
        grid.attach(Gtk.Label(label="Executed Process"), 6, 0, 5, 1)
        grid.attach(self.executed_process_label, 6, 1, 5, 1)
        grid.attach(Gtk.Label(label="Suspended Processes"), 6, 2, 5, 1)
        grid.attach(suspended_processes_scrolled_window, 6, 3, 5, 17)

        self.add(grid)

    def init_events(self):
        self.add_process_button.connect("clicked", self.add_process_action)

    def update_components(self):
        # Load processes -------------------------------------------------------
        inactive_processes = self.process_manager.inactive_processes
        prepared_processes = self.process_manager.prepared_processes
        executed_process = self.process_manager.executed_process
        suspended_processes = self.process_manager.suspended_processes

        # Clear lists ----------------------------------------------------------
        self.clear_list_box(self.inactive_processes_list_box)
        self.clear_list_box(self.prepared_processes_list_box)
        self.clear_list_box(self.suspended_processes_list_box)
        # Add processes to lists -----------------------------------------------
        for i in inactive_processes:
            row = Gtk.ListBoxRow()
            process_button = Gtk.ToggleButton(label=i.name)
            if i.is_active:
                process_button.set_active(True)
            process_button.connect("clicked", self.prepare_process_action)
            row.add(process_button)
            self.inactive_processes_list_box.add(row)

        for i in prepared_processes:
            row = Gtk.ListBoxRow()
            process_button = Gtk.ToggleButton(label=i.name)
            row.add(process_button)
            self.prepared_processes_list_box.add(row)

        if executed_process:
            self.executed_process_label.set_label(str(executed_process))

        for i in suspended_processes:
            row = Gtk.ListBoxRow()
            process_button = Gtk.ToggleButton(label=i.name)
            row.add(process_button)
            self.suspended_processes_list_box.add(row)

        # Update lists components ----------------------------------------------
        self.inactive_processes_list_box.show_all()
        self.prepared_processes_list_box.show_all()
        self.suspended_processes_list_box.show_all()

    def clear_list_box(self, list_box):
        for i in list_box.get_children():
            i.destroy()

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
        self.executing = True

        if button.get_active():
            process = self.process_manager.prepare_process(button.get_label())
            print(process, button.get_active())
            self.update_components()
        else:
            button.set_active(True)

    def execute_process_action(self, button):
        process = process_manager.search_process(
            button.get_name, self.process_manager.inactive_processes
        )
        self.process_manager.execute_process(process.pid)

    def deactivate_process_action(self, button):
        self.process_manager.deactivate_process()

    def suspend_process_action(self, button):
        self.process_manager.suspend_process()


if __name__ == "__main__":
    ProcessManagerWindow().show_all()
    Gtk.main()
