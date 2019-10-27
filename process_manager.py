from process import Process
import file_manager


class ProcessManager:
	def __init__(self):
		self.inactive_processes = self.load_processes()
		self.prepared_processes = []
		self.executed_process = None
		self.suspended_processes = []

	def load_processes(self) -> list:
		try:
			return file_manager.read_binary_file('processes.pcs')
		except FileNotFoundError as err:
			print(err)
		return []

	def search_process(self, data) -> Process:
		process = Process(data)
		for i in self.inactive_processes:
			if i == process:
				return i

	def add_process(self, process_name):
		process = Process(process_name)
		file_manager.append_binary_file('processes.pcs', process)
		self.inactive_processes.append(process)

	def prepare_process(self, process_name):
		process = self.search_process(process_name)
		process.activate()
		self.prepared_processes.append(process)

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
	
if __name__ == "__main__":
	processManager = ProcessManager()
	print(processManager.inactive_processes)