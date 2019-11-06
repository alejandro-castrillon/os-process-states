import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from process_manager import ProcessManager
from process import Process


class ProcessManagerWindow(Gtk.Window):
    def __init__(self) -> None:
        Gtk.Window.__init__(self, title='Process Manager')
        self.connect('destroy', Gtk.main_quit)

        self.executing = False
        self.process_manager = ProcessManager()

        self.init_components()

    def init_components(self) -> None:
        grid = Gtk.Grid(
            row_homogeneous=True,
            column_homogeneous=True,
            row_spacing=5,
            column_spacing=5,
        )

        # Process Button -------------------------------------------------------
        self.add_process_button = Gtk.Button(label='Add Process')
        self.add_process_button.connect('clicked', self.add_process_action)

        # Inactive Processes List ----------------------------------------------
        self.inactive_processes_list_box = Gtk.ListBox()
        self.inactive_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        inactive_processes_scrolled_window = Gtk.ScrolledWindow()
        inactive_processes_scrolled_window.add(self.inactive_processes_list_box)

        # Inactive Processes List ----------------------------------------------
        self.prepared_processes_list_box = Gtk.ListBox()
        self.prepared_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        prepared_processes_scrolled_window = Gtk.ScrolledWindow()
        prepared_processes_scrolled_window.add(self.prepared_processes_list_box)

        # Inactive Processes List ----------------------------------------------
        self.executed_process_label = Gtk.Label(label='None')
        self.executed_process_label.set_halign(Gtk.Align.CENTER)

        # Inactive Processes List ----------------------------------------------
        self.suspended_processes_list_box = Gtk.ListBox()
        self.suspended_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        suspended_processes_scrolled_window = Gtk.ScrolledWindow()
        suspended_processes_scrolled_window.add(
            self.suspended_processes_list_box
        )

        # Add Components -------------------------------------------------------
        grid.attach(Gtk.Label(label='Inactive Processes'), 0, 0, 1, 1)
        grid.attach(inactive_processes_scrolled_window, 0, 1, 1, 18)
        grid.attach(self.add_process_button, 0, 19, 1, 1)
        grid.attach(Gtk.Label(label='Prepared Processes'), 1, 0, 4, 1)
        grid.attach(prepared_processes_scrolled_window, 1, 1, 4, 19)
        grid.attach(Gtk.Label(label='Executed Process'), 5, 0, 4, 1)
        grid.attach(self.executed_process_label, 5, 1, 4, 1)
        grid.attach(Gtk.Label(label='Suspended Processes'), 5, 2, 4, 1)
        grid.attach(suspended_processes_scrolled_window, 5, 3, 4, 17)

        self.update_components()

        self.add(grid)

    def update_components(self) -> None:
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
            if i.pid:
                process_button.set_active(True)
            process_button.connect('clicked', self.prepare_process_action)
            row.add(process_button)
            self.inactive_processes_list_box.add(row)
            process_button = None

        for i in prepared_processes:
            row = Gtk.ListBoxRow()
            process_button = Gtk.Label(label=i.name)
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

    def clear_list_box(self, list_box) -> None:
        for i in list_box.get_children():
            i.destroy()

    def add_process_action(self, button) -> None:
        add_process_message_dialog = Gtk.MessageDialog(
            parent=self,
            title='Add New Process',
            text='Process Name:',
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

    def add_process(self, process_name) -> None:
        self.process_manager.add_process(process_name)
        self.update_components()

    def prepare_process_action(self, button) -> None:
        if button.get_active():
            process = self.process_manager.prepare_process(button.get_label())
            print(process, button.get_active())
            self.update_components()

            if not self.executing:
                self.executing = True
                self.compete_by_higher_priority()
        else:
            button.set_active(True)

    def execute_process_action(self, process) -> None:
        self.process_manager.execute_process(process.pid)
        self.update_components()

    def deactivate_process_action(self) -> None:
        self.process_manager.deactivate_process()
        self.update_components()

    def suspend_process_action(self) -> None:
        self.process_manager.suspend_process()
        self.update_components()

    def compete_by_higher_priority(self):
        prepared_processes = self.process_manager.prepared_processes

        higher_priority_processes = self.get_higher_priority_processes(
            prepared_processes
        )

        if higher_priority_processes:
            if len(higher_priority_processes) > 1:
                process_to_execute = self.compete_by_quantum(
                    higher_priority_processes
                )
            else:
                process_to_execute = higher_priority_processes[0]
        else:
            process_to_execute = self.compete_by_quantum(prepared_processes)

        self.execute_process_action(process_to_execute)

    def compete_by_quantum(self, processes) -> Process:
        lower_quantum_processes = self.get_lower_quantum_processes(processes)
        if lower_quantum_processes:
            if len(lower_quantum_processes) > 1:
                return self.get_lower_pid_process(lower_quantum_processes)
            else:
                return lower_quantum_processes[0]

    def get_higher_priority_processes(self, processes) -> list:
        higher_priority_processes = []
        for i in processes:
            if i.priority_level == 'VeryHigh':
                higher_priority_processes.append(i)
        return higher_priority_processes

    def get_lower_quantum_processes(self, processes) -> list:
        lower_quantum_processes = []
        lower_quantum = None, 0
        for i in processes:
            if lower_quantum[1] < i.quantum:
                lower_quantum = i, i.quantum
        for i in processes:
            if lower_quantum[1] == i.quantum:
                lower_quantum_processes.append(i)
        return lower_quantum_processes

    def get_lower_pid_process(self, processes) -> Process:
        lower_pip_process = None, 0
        for i in processes:
            if lower_pip_process[1] < i.pip:
                lower_pip_process = i, i.pip
        return lower_pip_process[0]


if __name__ == '__main__':
    ProcessManagerWindow().show_all()
    Gtk.main()
