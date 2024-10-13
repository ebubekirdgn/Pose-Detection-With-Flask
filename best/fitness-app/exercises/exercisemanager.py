from exercises.bicep_curl_strategy import BicepsCurlStrategy
from exercises.crunch_strategy import CrunchStrategy
from exercises.lateral_raise_strategy import LateralRaiseStrategy
from exercises.shoulder_press_strategy import ShoulderPressStrategy
from exercises.squat_strategy import SquatStrategy
from exercises.triceps_extension_strategy import TricepsExtensionStrategy


class ExerciseManager:
    def __init__(self):
        self.strategies = {}

    def get_strategy(self, exercise_name):
        # Egzersiz adı sözlükte yoksa yeni bir nesne oluştur
        if exercise_name not in self.strategies:
            if exercise_name == 'biceps_curl':
                self.strategies[exercise_name] = BicepsCurlStrategy()
            elif exercise_name == 'triceps_extension':
                self.strategies[exercise_name] = TricepsExtensionStrategy()
            elif exercise_name == 'lateral_raise':
                self.strategies[exercise_name] = LateralRaiseStrategy()
            elif exercise_name == 'squat':
                self.strategies[exercise_name] = SquatStrategy()
            elif exercise_name == 'shoulder_press':
                self.strategies[exercise_name] = ShoulderPressStrategy()
            elif exercise_name == 'crunch':
                self.strategies[exercise_name] = CrunchStrategy()
            else:
                raise ValueError(f"Geçersiz egzersiz adı: {exercise_name}")

        return self.strategies[exercise_name]
