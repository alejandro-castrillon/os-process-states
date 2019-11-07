import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from process_manager import ProcessManager
from process import Process


class ProcessManagerWindow(Gtk.Window):
    # __________________________________________________________________________
    def __init__(self) -> None:
        Gtk.Window.__init__(self, title='Process Manager')
        self.connect('destroy', Gtk.main_quit)
        self.set_border_width(5)

        self.process_manager = ProcessManager()
        self.timeout_id = None

        self.init_components()

    # __________________________________________________________________________
    def init_components(self) -> None:
        grid = Gtk.Grid(
            row_homogeneous=True,
            column_homogeneous=True,
            row_spacing=5,
            column_spacing=5,
        )

        # Simulate Switch ------------------------------------------------------
        top_box = Gtk.Box(spacing=2)

        self.simulating_label = Gtk.Label(label='Start Simulating')
        simulating_switch = Gtk.Switch()
        simulating_switch.connect('notify::active', self.execute_simulation)
        self.executing_spinner = Gtk.Spinner()

        # Inactive Processes List ----------------------------------------------
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.inactive_processes_list_box = Gtk.ListBox()
        self.inactive_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        inactive_processes_scrolled_window = Gtk.ScrolledWindow()
        inactive_processes_scrolled_window.add(self.inactive_processes_list_box)

        add_process_button = Gtk.Button(label='Add Process')
        add_process_button.connect('clicked', self.add_process_action)

        # Prepared Processes List ----------------------------------------------
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.prepared_processes_list_box = Gtk.ListBox()
        self.prepared_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        prepared_processes_scrolled_window = Gtk.ScrolledWindow()
        prepared_processes_scrolled_window.add(self.prepared_processes_list_box)

        # Executed Process Progress Bar ----------------------------------------
        self.executed_process_progress_bar = Gtk.ProgressBar()
        self.executed_process_progress_bar.set_text('')
        self.executed_process_progress_bar.set_show_text(True)
        flow_box = Gtk.ListBox()
        flow_box.add(self.executed_process_progress_bar)

        # Suspended Processes List ---------------------------------------------
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        self.suspended_processes_list_box = Gtk.ListBox()
        self.suspended_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        suspended_processes_scrolled_window = Gtk.ScrolledWindow()
        suspended_processes_scrolled_window.add(
            self.suspended_processes_list_box
        )

        # Add Components -------------------------------------------------------
        top_box.add(self.simulating_label)
        top_box.add(simulating_switch)
        top_box.add(self.executing_spinner)

        grid.attach(top_box, 0, 0, 3, 1)

        grid.attach(Gtk.Label(label='Inactive Processes'), 0, 1, 1, 1)
        grid.attach(inactive_processes_scrolled_window, 0, 2, 1, 17)
        grid.attach(add_process_button, 0, 19, 1, 1)

        grid.attach(Gtk.Label(label='Prepared Processes'), 1, 1, 3, 1)
        grid.attach(prepared_processes_scrolled_window, 1, 2, 3, 18)

        grid.attach(Gtk.Label(label='Executed Process'), 4, 1, 3, 1)
        grid.attach(flow_box, 4, 2, 3, 1)

        grid.attach(Gtk.Label(label='Suspended Processes'), 4, 3, 3, 1)
        grid.attach(suspended_processes_scrolled_window, 4, 4, 3, 16)

        self.update_components()
        self.add(grid)

    # __________________________________________________________________________
    def update_components(self) -> None:
        # Clear lists ----------------------------------------------------------
        self.clear_list_box(self.inactive_processes_list_box)
        self.clear_list_box(self.prepared_processes_list_box)
        self.clear_list_box(self.suspended_processes_list_box)

        # Add Inactive Processes -----------------------------------------------
        for i in self.process_manager.inactive_processes:
            row = Gtk.ListBoxRow()
            process_button = Gtk.ToggleButton(label=i.name)
            if i.pid:
                process_button.set_active(True)
            process_button.connect('clicked', self.prepare_process_action)
            row.add(process_button)
            self.inactive_processes_list_box.add(row)

        # Add Prepared Processes -----------------------------------------------
        for i in self.process_manager.prepared_processes:
            row = Gtk.ListBoxRow()
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_text(str(i))
            progress_bar.set_show_text(True)
            row.add(progress_bar)
            self.prepared_processes_list_box.add(row)

        # Add Executed Processes -----------------------------------------------
        executed_process = self.process_manager.executed_process
        if executed_process:
            self.executed_process_progress_bar.set_text(str(executed_process))

        # Add Suspended Processes ----------------------------------------------
        for i in self.process_manager.suspended_processes:
            row = Gtk.ListBoxRow()
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_text(str(i))
            progress_bar.set_show_text(True)
            row.add(progress_bar)
            self.suspended_processes_list_box.add(row)

        # Update lists components ----------------------------------------------
        self.inactive_processes_list_box.show_all()
        self.prepared_processes_list_box.show_all()
        self.suspended_processes_list_box.show_all()

    # __________________________________________________________________________
    def clear_list_box(self, list_box) -> None:
        for i in list_box.get_children():
            i.destroy()

    # __________________________________________________________________________
    def execute_simulation(self, switch, gparam):
        if switch.get_active():
            self.timeout_id = GLib.timeout_add(
                1000, self.compete_by_higher_priority, None
            )
            self.executing_spinner.start()
            self.simulating_label.set_label("Stop Simulating")
        else:
            if self.timeout_id:
                GLib.source_remove(self.timeout_id)
                self.timeout_id = None
            self.executing_spinner.stop()
            self.simulating_label.set_label("Start Simulating")

    # __________________________________________________________________________
    def add_process_action(self, button) -> None:
        add_process_message_dialog = Gtk.MessageDialog(
            parent=None,
            title='Add New Process',
            text='Process Name:',
            secondary_text='Empty name will not be added',
            buttons=Gtk.ButtonsType.OK_CANCEL,
        )

        process_name_entry = Gtk.Entry()
        add_process_message_dialog.get_content_area().pack_end(
            process_name_entry, True, True, 0
        )

        add_process_message_dialog.show_all()
        response = add_process_message_dialog.run()
        process_name = process_name_entry.get_text()
        add_process_message_dialog.destroy()

        if process_name and response == Gtk.ResponseType.OK:
            self.add_process(process_name)

    # __________________________________________________________________________
    def add_process(self, process_name) -> None:
        self.process_manager.add_process(process_name)
        self.update_components()

    # __________________________________________________________________________
    def prepare_process_action(self, button) -> None:
        if button.get_active():
            process = self.process_manager.prepare_process(button.get_label())
            if process:
                print('+ prepare:', process)
                self.update_components()
            else:
                show_error_message_error = Gtk.MessageDialog(
                    parent=None,
                    title='Can not execute more processes',
                    text='Error:',
                    secondary_text='Can not execute more processes\nProcesses Limit: 999',
                    buttons=Gtk.ButtonsType.OK_CANCEL,
                )
                response = show_error_message_error.run()
                show_error_message_error.destroy()
        else:
            button.set_active(True)

    # __________________________________________________________________________
    def execute_process_action(self, process) -> None:
        print('* execute:', process)
        self.process_manager.execute_process(process)
        self.update_components()

    # __________________________________________________________________________
    def deactivate_process_action(self) -> None:
        process = self.process_manager.deactivate_process()
        print('- deactivate:', process)
        self.update_components()

    # __________________________________________________________________________
    def suspend_process_action(self) -> None:
        process = self.process_manager.suspend_process()
        print('/ suspend:', process)
        self.update_components()

    # __________________________________________________________________________
    def compete_by_higher_priority(self, button):
        prepared_processes = self.process_manager.prepared_processes

        if prepared_processes:
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
        return True

    # __________________________________________________________________________
    def compete_by_quantum(self, processes) -> Process:
        lower_quantum_processes = self.get_lower_quantum_processes(processes)
        if lower_quantum_processes:
            if len(lower_quantum_processes) > 1:
                lower_pid_process = self.get_lower_pid_process(
                    lower_quantum_processes
                )
                return lower_pid_process
            else:
                return lower_quantum_processes[0]

    # __________________________________________________________________________
    def get_higher_priority_processes(self, processes) -> list:
        higher_priority_processes = []
        for i in processes:
            if i.priority == 'VeryHigh':
                higher_priority_processes.append(i)
        return higher_priority_processes

    # __________________________________________________________________________
    def get_lower_quantum_processes(self, processes) -> list:
        lower_quantum_processes = []
        lower_quantum = None, 51
        for i in processes:
            if lower_quantum[1] > i.quantum:
                lower_quantum = i, i.quantum
        for i in processes:
            if lower_quantum[1] == i.quantum:
                lower_quantum_processes.append(i)
        return lower_quantum_processes

    # __________________________________________________________________________
    def get_lower_pid_process(self, processes) -> Process:
        lower_pip_process = None, 1000
        for i in processes:
            if lower_pip_process[1] > int(i.pid):
                lower_pip_process = i, int(i.pid)
        return lower_pip_process[0]


if __name__ == '__main__':
    ProcessManagerWindow().show_all()
    Gtk.main()
