from exercises.exercise_strategy import ExerciseStrategy

class TricepsExtensionStrategy(ExerciseStrategy):
    def perform_exercise(self):
        print("TricepsExtensionStrategy")
    
    def get_totals(self, user):
        return self.get_total_exercises(user)  # Ortak metodu kullan   
