import random


class Process:
    def __init__(self, name):
        self.name = name
        self.name_pad = 0
        self.deactivate()

    def activate(self, pid):
        self.pid = pid
        self.priority = random.choice(["VeryHigh", "High", "Medium", "Low"])
        self.memory = random.randint(100, 300)
        self.quantum = random.randint(10, 50)
        self.progress = 0
        self.interaction = random.choice([True, False])

    def deactivate(self):
        self.pid = None
        self.priority = None
        self.memory = None
        self.quantum = None
        self.progress = None
        self.interaction = None

    def __str__(self):
        string = f"Process(name={self.name:<{self.name_pad}}"
        if self.pid:
            string += (
                f", pid={self.pid:0>3}"
                f", priority={self.priority:<8}"
                f", memory={self.memory}"
                f", quantum={self.quantum}"
                f", interaction={str(self.interaction):<5}"
            )
        return string + ")"

    def __repr__(self):
        return str(self)

    def __eq__(self, process):
        return isinstance(process, Process) and int(self.pid) == int(process.pid)
