from process import Process
import file_manager


class ProcessManager:
    # __________________________________________________________________________
    def __init__(self):
        self.inactive_processes = self.load_processes()
        self.prepared_processes = []
        self.executed_process = None
        self.suspended_processes = []

        self.quantum_rat = 0
        self.current_pid = 0

    # __________________________________________________________________________
    def load_processes(self) -> list:
        try:
            processes = file_manager.read_binary_file('processes.pcs')
        except FileNotFoundError as err:
            print(err)
            self.inactive_processes = []
            for i in file_manager.read_file('processes_names.txt'):
                self.add_process(i)
            processes = self.load_processes()
        self.name_pad = max([len(i.name) for i in processes])
        return processes

    # __________________________________________________________________________
    def add_process(self, process_name) -> None:
        process = Process(process_name)
        file_manager.append_binary_file('processes.pcs', process)
        self.inactive_processes.append(process)

    # __________________________________________________________________________
    def prepare_process(self, process_name) -> Process:
        process = Process(process_name)
        process.name_pad = self.name_pad
        if len(self.prepared_processes) < 1000:
            process.activate(self.generate_pid())
            self.prepared_processes.append(process)
            return process

    # __________________________________________________________________________
    def execute_process(self, process) -> None:
        self.executed_process = process
        self.prepared_processes.remove(process)

    def deactivate_process(self) -> Process:
        self.executed_process.deactivate()
        process, self.executed_process = self.executed_process = None
        return process

    # __________________________________________________________________________
    def suspend_process(self) -> Process:
        self.suspended_processes.append(self.executed_process)
        process, self.executed_process = self.executed_process = None
        return process

    # __________________________________________________________________________
    def generate_pid(self):
        self.current_pid = str(int(self.current_pid) + 1)
        return self.current_pid
