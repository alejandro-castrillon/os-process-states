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
            return file_manager.read_binary_file("processes.pcs")
        except FileNotFoundError as err:
            print(err)
            processes = []
            for i in ['bash', 'nano', 'git', 'python']:
                processes += [Process(i)]
            return processes

    def add_process(self, process_name):
        process = Process(process_name)
        file_manager.append_binary_file("processes.pcs", process)
        self.inactive_processes.append(process)

    def prepare_process(self, process_name):
        process = None
        for i in self.inactive_processes:
            if i.name == process_name:
                process = i
        if process:
            process.activate(self.generate_pid())
            self.prepared_processes.append(process)
            return process

    def execute_process(self, process_pid):
        process = None
        for i in self.prepared_processes:
            if i.pid == process_pid:
                process = i
        self.prepared_processes.remove(process)
        self.execute_process = process

    def deactivate_process(self):
        self.executed_process.deactivate()
        self.execute_process = None

    def suspend_process(self):
        self.suspended_processes.append(self.executed_process)
        self.executed_process = None

    def generate_pid(self):
        self.current_pid = str(int(self.current_pid) + 1)
        while len(self.current_pid) < 4:
            self.current_pid = '0' + self.current_pid
        return self.current_pid
