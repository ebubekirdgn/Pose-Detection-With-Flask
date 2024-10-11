from exercises.exercise_strategy import ExerciseStrategy

class SquatStrategy(ExerciseStrategy):
    def perform_exercise(self):
        print("SquatStrategy")

    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan   
