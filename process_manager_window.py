import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from process_manager import ProcessManager
from process_progress_bar import ProcessProgressBar
from process import Process

class Row(Gtk.ListBoxRow):
    def __init__(self, progress_bar):
        super().__init__()
        super().add(progress_bar)
        self.process = progress_bar.process

class ProcessManagerWindow(Gtk.Window):
    # __________________________________________________________________________
    def __init__(self) -> None:
        super().__init__(title="Process Manager")
        self.connect("destroy", Gtk.main_quit)
        self.set_border_width(5)

        self.expropiated_process: Process = None
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

        self.simulating_label = Gtk.Label(label="Start Simulating")
        self.simulating_switch = Gtk.Switch()
        self.simulating_switch.set_active(False)
        self.simulating_switch.connect("notify::active", self.execute_simulation)
        self.executing_spinner = Gtk.Spinner()
        self.quantum_rat_spin_button = Gtk.SpinButton(
            adjustment=Gtk.Adjustment(
                value=750,
                lower=125,
                upper=10000,
                step_increment=125,
                page_increment=0,
                page_size=0
            ), climb_rate=1, digits=0,
        )
        self.quantum_rat_spin_button.connect("value-changed", self.change_quantum_rat)

        # Inactive Processes List ----------------------------------------------
        self.inactive_processes_list_box = Gtk.ListBox()
        self.inactive_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        inactive_processes_scrolled_window = Gtk.ScrolledWindow()
        inactive_processes_scrolled_window.add(self.inactive_processes_list_box)

        for i in self.process_manager.inactive_processes:
            process_button = Gtk.Button(label=i.name)
            process_button.connect("clicked", self.prepare_process_action)
            self.inactive_processes_list_box.add(process_button)

        add_process_button = Gtk.Button(label="Add Process")
        add_process_button.connect("clicked", self.add_process_action)

        # Prepared Processes List ----------------------------------------------
        self.prepared_processes_list_box = Gtk.ListBox()
        self.prepared_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        prepared_processes_scrolled_window = Gtk.ScrolledWindow()
        prepared_processes_scrolled_window.add(self.prepared_processes_list_box)

        # Executed Process Progress Bar ----------------------------------------
        self.executed_process_list_box = Gtk.ListBox()
        self.executed_process_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        executed_process_scrolled_window = Gtk.ScrolledWindow()
        executed_process_scrolled_window.add(self.executed_process_list_box)

        # Suspended Processes List ---------------------------------------------
        self.suspended_processes_list_box = Gtk.ListBox()
        self.suspended_processes_list_box.set_selection_mode(
            Gtk.SelectionMode.NONE
        )
        suspended_processes_scrolled_window = Gtk.ScrolledWindow()
        suspended_processes_scrolled_window.add(
            self.suspended_processes_list_box
        )

        # Add Components -------------------------------------------------------
        top_box.add(Gtk.Label(label='Quantum Rat (ms):'))
        top_box.add(self.quantum_rat_spin_button)
        top_box.add(self.simulating_label)
        top_box.add(self.simulating_switch)
        top_box.add(self.executing_spinner)

        grid.attach(top_box, 0, 0, 3, 1)

        grid.attach(Gtk.Label(label="Inactive Processes"), 0, 1, 1, 1)
        grid.attach(inactive_processes_scrolled_window, 0, 2, 1, 15)
        grid.attach(add_process_button, 0, 17, 1, 1)

        grid.attach(Gtk.Label(label="Prepared Processes"), 1, 1, 3, 1)
        grid.attach(prepared_processes_scrolled_window, 1, 2, 3, 16)

        grid.attach(Gtk.Label(label="Executed Process"), 4, 1, 3, 1)
        grid.attach(executed_process_scrolled_window, 4, 2, 3, 1)

        grid.attach(Gtk.Label(label="Suspended Processes"), 4, 3, 3, 1)
        grid.attach(suspended_processes_scrolled_window, 4, 4, 3, 14)

        self.update_components()
        self.add(grid)

    # __________________________________________________________________________
    def update_components(self) -> None:
        # Add Prepared Processes -----------------------------------------------
        self.remove_list_box(
            self.process_manager.prepared_processes,
            self.prepared_processes_list_box
        )
        for i in self.process_manager.prepared_processes:
            process_progress_bar = ProcessProgressBar(i)
            
            flag = True
            for j in self.prepared_processes_list_box.get_children():
                if j.process == i:
                    flag = False
                    break
            if flag:
                self.prepared_processes_list_box.add(Row(process_progress_bar))

        # Add Executed Processes -----------------------------------------------
        executed_process = self.process_manager.executed_process
        self.clear_list_box(self.executed_process_list_box)
        if executed_process:
            process_progress_bar = ProcessProgressBar(executed_process)
            self.executed_process_list_box.add(process_progress_bar)

        # Add Suspended Processes ----------------------------------------------
        self.remove_list_box(
            self.process_manager.suspended_processes,
            self.suspended_processes_list_box
        )
        for i in self.process_manager.suspended_processes:
            process_progress_bar = ProcessProgressBar(i)
            
            flag = True
            for j in self.suspended_processes_list_box.get_children():
                if j.process == i:
                    flag = False
                    break
            if flag:
                self.suspended_processes_list_box.add(Row(process_progress_bar))

        # Update lists components ----------------------------------------------
        self.inactive_processes_list_box.show_all()
        self.prepared_processes_list_box.show_all()
        self.executed_process_list_box.show_all()
        self.suspended_processes_list_box.show_all()

    # __________________________________________________________________________
    def remove_list_box(self, processes_list, list_box):
        for i in list_box.get_children():
            if i.process not in processes_list:
                i.destroy()
    # __________________________________________________________________________
    def clear_list_box(self, list_box) -> None:
        for i in list_box.get_children():
            i.destroy()

    # __________________________________________________________________________
    def execute_simulation(self, switch, _):
        f = self.complete_execution if self.expropiated_process else self.iteration

        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
        del self.timeout_id
        self.timeout_id = None

        if switch.get_active():
            self.timeout_id = GLib.timeout_add(
                self.process_manager.quantum_rat * 1000, f, None
            )
            self.executing_spinner.start()
            self.simulating_label.set_label("Stop Simulating")
        else:
            self.executing_spinner.stop()
            self.simulating_label.set_label("Start Simulating")

    # __________________________________________________________________________
    def change_quantum_rat(self, spin_button):
        quantum_rat = spin_button.get_value_as_int()
        self.process_manager.set_quantum_rat(quantum_rat / 1000)
        
    # __________________________________________________________________________
    def add_process_action(self, _) -> None:
        add_process_message_dialog = Gtk.MessageDialog(
            parent=None,
            title="Add New Process",
            text="Process Name:",
            secondary_text="Empty name will not be added",
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
            self.process_manager.add_process(process_name)
            process_button = Gtk.Button(label=process_name)
            process_button.connect("clicked", self.prepare_process_action)
            self.inactive_processes_list_box.add(process_button)
            self.update_components()

    # __________________________________________________________________________
    def prepare_process_action(self, button) -> None:
        process = self.process_manager.prepare_process(button.get_label())
        if process:
            print("+ prepare:", process.__str__(True))

            if (process.priority == Process.PRIORITIES[0]
                and not self.expropiated_process):
                self.expropiation(process)

            self.update_components()
        else:
            show_error_message_error = Gtk.MessageDialog(
                parent=None,
                title="Can not execute more processes",
                text="Error:",
                secondary_text="Can not execute more processes\n"
                "Processes Limit: 999",
                buttons=Gtk.ButtonsType.OK_CANCEL,
            )
            show_error_message_error.run()
            show_error_message_error.destroy()

    # __________________________________________________________________________
    def execute_process_action(self, process) -> None:
        if process:
            print("* execute:", process.__str__(True))
            self.process_manager.execute_process(process)
            self.update_components()

    # __________________________________________________________________________
    def deactivate_process_action(self) -> None:
        process = self.process_manager.deactivate_process()
        print("- deactivate:", process.__str__(True))
        self.update_components()

    # __________________________________________________________________________
    def suspend_process_action(self) -> None:
        process = self.process_manager.suspend_process()
        print("/ suspend:", process.__str__(True))
        self.update_components()

    # __________________________________________________________________________
    def iteration(self, _) -> bool:
        # Suspended to prepared
        i = 0
        while i < len(self.process_manager.suspended_processes):
            process = self.process_manager.suspended_processes[0]
            if hasattr(process, 'next') and process.next:
                delattr(process, 'next')
                self.process_manager.suspended_processes.remove(process)
                self.process_manager.prepared_processes.append(process)
            elif process.interaction:
                process.next = True
                i += 1
            else:
                self.process_manager.suspended_processes.remove(process)
                self.process_manager.prepared_processes.append(process)
                
        # Executed to suspended or deactivated
        executed_process = self.process_manager.executed_process
        if executed_process:
            executed_process.progress += executed_process.advance
            if executed_process.progress >= 1:
                self.deactivate_process_action()
            else:
                self.suspend_process_action()

        # Prepared to executed
        process_to_execute = self.process_manager.compete()
        self.execute_process_action(process_to_execute)

        return self.expropiated_process == None

    # __________________________________________________________________________
    def expropiation(self, process: Process) -> None:
        executed = self.process_manager.executed_process
        if executed:
            self.process_manager.prepared_processes.append(executed)
            self.process_manager.execute_process(process)

            self.expropiated_process = process
            self.execute_simulation(self.simulating_switch, None)

        print("^ expropiate:", process.__str__(True))
        self.process_manager.execute_process(process)

        self.expropiated_process = process
        self.execute_simulation(self.simulating_switch, None)

    # __________________________________________________________________________
    def complete_execution(self, _) -> bool:
        # Execute until complete, then deactivate
        executed_process = self.process_manager.executed_process
        if executed_process:
            executed_process.progress += executed_process.advance
            print("* execute:", executed_process.__str__(True))

            if executed_process.progress >= 1:
                self.deactivate_process_action()
                del self.expropiated_process
                self.expropiated_process = None
                self.execute_simulation(self.simulating_switch, None)

        self.update_components()
        return self.expropiated_process != None

if __name__ == "__main__":
    os.system('clear')
    ProcessManagerWindow().show_all()
    Gtk.main()
