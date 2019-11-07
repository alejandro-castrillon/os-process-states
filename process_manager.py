from process import Process
import file_manager


class ProcessManager:
    def __init__(self):
        self.inactive_processes = self.load_processes()
        self.prepared_processes = []
        self.executed_process = None
        self.suspended_processes = []

        self.quantum_rat = 0
        self.current_pid = '0000'

    def load_processes(self) -> list:
        try:
            return file_manager.read_binary_file('processes.pcs')
        except FileNotFoundError as err:
            print(err)
            self.inactive_processes = []
            for i in file_manager.read_file('processes_names.txt'):
                self.add_process(i)
            return self.load_processes()

    def add_process(self, process_name):
        process = Process(process_name)
        file_manager.append_binary_file('processes.pcs', process)
        self.inactive_processes.append(process)

    def prepare_process(self, process_name) -> Process:
        process = None
        for i in self.inactive_processes:
            if i.name == process_name:
                process = i
        if process:
            process.activate(self.generate_pid())
            self.prepared_processes.append(process)
            return process

    def execute_process(self, process) -> None:
        self.prepared_processes.remove(process)
        self.executed_process = process

    def deactivate_process(self) -> Process:
        self.executed_process.deactivate()
        process, self.execute_process = self.execute_process = None
        return process

    def suspend_process(self) -> Process:
        self.suspended_processes.append(self.executed_process)
        self.executed_process = None

    def generate_pid(self):
        self.current_pid = str(int(self.current_pid) + 1)
        while len(self.current_pid) < 4:
            self.current_pid = '0' + self.current_pid
        return self.current_pid
