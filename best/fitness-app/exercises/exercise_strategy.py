from abc import ABC, abstractmethod
import sqlite3

class ExerciseStrategy(ABC):
    @abstractmethod
    def perform_exercise(self):
        pass
    
    def get_total_exercises(self, user):
        # Bu fonksiyon, tüm hareketlerin toplamını getirir
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Her hareket için toplam sayıları al
        cursor.execute('''
            SELECT
                SUM(biceps_curl) AS total_biceps_curl,
                SUM(triceps_extension) AS total_triceps_extension,
                SUM(lateral_raise) AS total_lateral_raise,
                SUM(squat) AS total_squat,
                SUM(shoulder_press) AS total_shoulder_press,
                SUM(crunch) AS total_crunch
            FROM exercises
            WHERE user = ?
        ''', (user,))
        
        totals = cursor.fetchone()
        conn.close()
        
        return {
            'total_biceps_curl': totals[0] or 0,
            'total_triceps_extension': totals[1] or 0,
            'total_lateral_raise': totals[2] or 0,
            'total_squat': totals[3] or 0,
            'total_shoulder_press': totals[4] or 0,
            'total_crunch': totals[5] or 0,
        }