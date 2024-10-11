from exercises.exercise_strategy import ExerciseStrategy

class LateralRaiseStrategy(ExerciseStrategy):
    def perform_exercise(self):
        print("LateralRaiseStrategy")

    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan   
