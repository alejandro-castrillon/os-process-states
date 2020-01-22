from process import Process
import file_manager


class ProcessManager:
    PROCESSES_FILE = 'processes.pcs'
    DEFAULT_PROCESSES_FILE = 'processes_names.txt'

    # __________________________________________________________________________
    def __init__(self):
        self.inactive_processes = self.load_processes()
        self.prepared_processes = []
        self.executed_process = None
        self.suspended_processes = []

        self.quantum_rat = 1
        self.current_pid = 0

    # __________________________________________________________________________
    def load_processes(self) -> list:
        try:
            processes = file_manager.read_binary_file(self.PROCESSES_FILE)
        except FileNotFoundError as err:
            print(err)
            self.inactive_processes = []
            for i in file_manager.read_file(self.DEFAULT_PROCESSES_FILE):
                self.add_process(i)
            processes = self.load_processes()
        self.name_pad = max([len(i.name) for i in processes])
        return processes

    # __________________________________________________________________________
    def add_process(self, process_name: str) -> None:
        process = Process(process_name)
        file_manager.append_binary_file(self.PROCESSES_FILE, process)
        self.inactive_processes.append(process)

    # __________________________________________________________________________
    def set_quantum_rat(self, quantum_rat: int):
        self.quantum_rat = quantum_rat
        for i in self.prepared_processes:
            i.quantum = i.processor_time / self.quantum_rat
            i.advance = 1 / i.quantum
        if self.executed_process:
            self.executed_process.quantum = (
                self.executed_process.processor_time / self.quantum_rat
            )
            self.executed_process.advance = 1 / self.executed_process.quantum
        for i in self.suspended_processes:
            i.quantum = i.processor_time / self.quantum_rat
            i.advance = 1 / i.quantum

    # __________________________________________________________________________
    def prepare_process(self, process_name: str) -> Process:
        process = Process(process_name)
        process.name_pad = self.name_pad
        if len(self.prepared_processes) < 1000:
            process.activate(self.generate_pid(), self.quantum_rat)
            self.prepared_processes.append(process)
            return process

    # __________________________________________________________________________
    def execute_process(self, process: Process) -> None:
        self.executed_process = process
        self.prepared_processes.remove(process)

    # __________________________________________________________________________
    def deactivate_process(self) -> Process:
        self.executed_process.deactivate()
        process, self.executed_process = self.executed_process, None
        return process

    # __________________________________________________________________________
    def suspend_process(self) -> Process:
        self.suspended_processes.append(self.executed_process)
        process, self.executed_process = self.executed_process, None
        return process

    # __________________________________________________________________________
    def generate_pid(self):
        self.current_pid = str(int(self.current_pid) + 1)
        return self.current_pid

    # __________________________________________________________________________
    def compete(self) -> Process:
        prepared_processes = self.prepared_processes

        if prepared_processes:
            # Expropiation
            high_priority_processes = self.get_high_priority_processes(
                prepared_processes
            )
            if high_priority_processes:
                if len(high_priority_processes) > 1:
                    return self.compete_by_quantum(high_priority_processes)
                else:
                    return high_priority_processes[0]
            else:
                return self.compete_by_quantum(prepared_processes)

    # __________________________________________________________________________
    def compete_by_quantum(self, processes:list) -> Process:
        lower_quantum_processes = self.get_lower_quantum_processes(processes)
        if lower_quantum_processes:
            if len(lower_quantum_processes) > 1:

                higher_priority_processes = self.get_higher_priority_processes(
                    lower_quantum_processes
                )[0]
                if higher_priority_processes:
                    if len(higher_priority_processes) > 1:
                        return self.get_lower_pid_process(
                            higher_priority_processes
                        )
                    else:
                        return higher_priority_processes[0]
            else:
                return lower_quantum_processes[0]

    # __________________________________________________________________________
    def get_high_priority_processes(self, processes:list) -> list:
        high_priority_processes = []
        for i in processes:
            if i.priority == Process.PRIORITIES[0]:
                high_priority_processes += [i]
        return high_priority_processes

    # __________________________________________________________________________
    def get_lower_quantum_processes(self, processes:list) -> list:
        lower_quantum_processes = []
        lower_quantum = None, 400
        for i in processes:
            if lower_quantum[1] >= i.quantum:
                lower_quantum = i, i.quantum
        for i in processes:
            if lower_quantum[1] == i.quantum:
                lower_quantum_processes.append(i)
        return lower_quantum_processes

    # __________________________________________________________________________
    def get_higher_priority_processes(self, processes:list) -> list:
        higher_priority_processes = []
        for i in Process.PRIORITIES:
            for j in processes:
                if j.priority == i:
                    higher_priority_processes += [j]
            if higher_priority_processes:
                return higher_priority_processes, i

    # __________________________________________________________________________
    def get_lower_pid_process(self, processes:list) -> Process:
        lower_pip_process = None, 1000
        for i in processes:
            if lower_pip_process[1] > int(i.pid):
                lower_pip_process = i, int(i.pid)
        return lower_pip_process[0]
