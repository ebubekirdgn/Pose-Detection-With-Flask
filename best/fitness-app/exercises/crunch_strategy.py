from exercises.exercise_strategy import ExerciseStrategy

class CrunchStrategy(ExerciseStrategy):
    def perform_exercise(self):
        print("CrunchStrategy")

    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan   
