from process import Process
import file_manager


class ProcessManager:
    def __init__(self):
        self.quantum_rat = 0
        self.inactive_processes = self.load_processes()
        self.prepared_processes = []
        self.executed_process = None
        self.suspended_processes = []

        self.current_pid = 1

    def load_processes(self) -> list:
        try:
            return file_manager.read_binary_file("processes.pcs")
        except FileNotFoundError as err:
            print(err)
        return []

    def search_process(self, data, _list) -> Process:
        process = Process(data)
        for i in _list:
            if i == process:
                return i

    def add_process(self, process_name):
        process = Process(process_name)
        file_manager.append_binary_file("processes.pcs", process)
        self.inactive_processes.append(process)

    def prepare_process(self, process_name):
        process = self.search_process(process_name, self.inactive_processes)
        if process:
            process.activate(self.current_pid)
            self.current_pid += 1
            self.prepared_processes.append(process)
            return process

    def execute_process(self, process_pid):
        process = self.search_process(process_pid)
        self.prepared_processes.remove(process_pid)
        self.execute_process = process

    def deactivate_process(self):
        self.executed_process.deactivate()
        self.execute_process = None

    def suspend_process(self):
        self.suspended_processes.append(self.executed_process)
        self.executed_process = None
