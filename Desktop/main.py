import tkinter as tk
from tkinter import ttk
import biceps_curl

# Hareket seçimi için işlev
def run_selected_exercise():
    selected_exercise = exercise_combobox.get()
    if selected_exercise == "Biceps Curl":
        biceps_curl.run()
    elif selected_exercise == "Triceps Extension":
        triceps_extension.run()
    elif selected_exercise == "Lateral Raise":
        lateral_raise.run()
    elif selected_exercise == "Squat":
        squat.run()
    elif selected_exercise == "Shoulder Press":
        shoulder_press.run()
    elif selected_exercise == "Mekik":
        mekik.run()
    else:
        print("Hareket seçilmedi.")

# Ana pencere
root = tk.Tk()
root.title("Sporcu Hareket Seçimi")

# Açılır menü
exercise_label = tk.Label(root, text="Bir hareket seçin:")
exercise_label.pack(pady=10)

exercises = ["Biceps Curl", "Triceps Extension", "Lateral Raise", "Squat", "Shoulder Press", "Mekik"]
exercise_combobox = ttk.Combobox(root, values=exercises)
exercise_combobox.pack(pady=10)

# Başlat butonu
start_button = tk.Button(root, text="Başlat", command=run_selected_exercise)
start_button.pack(pady=20)

# Ana döngü
root.mainloop()
