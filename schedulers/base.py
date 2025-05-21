from abc import ABC, abstractmethod

class SchedulerBase(ABC):
    @abstractmethod
    def add_process(self, process):
        pass

    @abstractmethod
    def get_next_process(self, current_time):
        pass