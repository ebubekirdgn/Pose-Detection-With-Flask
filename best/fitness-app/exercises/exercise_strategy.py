from abc import ABC, abstractmethod

class ExerciseStrategy(ABC):
    @abstractmethod
    def perform_exercise(self):
        pass
