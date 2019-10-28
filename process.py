import random


class Process:
    def __init__(self, name):
        self.name = name
        self.deactivate()

    def activate(self, pid):
        self.pid = pid
        self.priority_level = random.choice(["MA", "A", "M", "B"])
        self.memory = random.randint(100, 300)
        self.quantum = random.randint(10, 50)
        self.interaction = random.choice([True, False])

    def deactivate(self):
        self.pid = None
        self.priority_level = None
        self.memory = None
        self.quantum = None
        self.interaction = None

    def __str__(self):
        string = f"Process[name={self.name}"
        if self.pid:
            string += (
                f", pid={self.pid}, "
                f"priority_level={self.priority_level}, "
                f"memory={self.memory}, "
                f"quantum={self.quantum}, "
                f"interaction={self.interaction}"
            )
        return string + "]"

    def __eq__(self, process):
        return isinstance(process, Process) and (
            process.name == self.name or process.pid == self.pid
        )
