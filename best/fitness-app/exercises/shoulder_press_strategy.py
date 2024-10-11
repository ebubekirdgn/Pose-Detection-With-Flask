from exercises.exercise_strategy import ExerciseStrategy

class ShoulderPressStrategy(ExerciseStrategy):
    def perform_exercise(self):
        print("ShoulderPressStrategy")

    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan   
