import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from utilities import trunc

class ProcessProgressBar(Gtk.EventBox):
    def __init__(self, process):
        super().__init__()

        self.process = process

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        if process:
            self.progress_bar.set_text(str(process))
            self.progress_bar.set_fraction(self.process.progress)
        self.add(self.progress_bar)

        self.connect('button_press_event', self.show_process)

    def show_process(self, button, _):
        popover = Gtk.Popover()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(Gtk.Label(label=f'Name: {self.process.name}'))
        box.add(Gtk.Label(label=f'PID: {self.process.pid}'))
        box.add(Gtk.Label(label=f'Priority: {self.process.priority}'))
        box.add(Gtk.Label(label=f'Memory: {self.process.memory}'))
        box.add(Gtk.Label(label=f'Processor Time: {self.process.processor_time}'))
        box.add(Gtk.Label(label=f'Quantum: {round(self.process.quantum, 4)}'))
        box.add(Gtk.Label(label=f'Progress: {trunc(self.process.progress * 100, 4)}%'))
        box.add(Gtk.Label(label=f'Interaction: {self.process.interaction}'))

        popover.add(box)
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.set_relative_to(self.progress_bar)
        popover.show_all()
        popover.popup()
