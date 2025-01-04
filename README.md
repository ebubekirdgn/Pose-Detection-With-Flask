# Pose Detection with Flask

## About the Project
Pose Detection with Flask is a fitness-focused application that uses pose estimation techniques to help users maintain proper form during exercises. The project leverages the **Strategy Design Pattern** to provide a flexible and scalable approach to analyzing and providing feedback on various exercises.

## Features
- Real-time pose detection using a webcam or uploaded video.
- Feedback on exercise form and posture.
- Scalable design with support for multiple exercise types.
- Modular implementation using the Strategy Design Pattern.

## Built With
- **Flask**: A lightweight WSGI web application framework.
- **MediaPipe**: A framework for building multimodal applied ML pipelines, used for pose estimation.
- **JavaScript**: For handling frontend interactivity.
- **HTML/CSS**: For creating the user interface.
- **Python**: Backend implementation and pose analysis logic.

## Strategy Design Pattern
The Strategy Design Pattern is used to handle multiple exercise types and their specific analysis logic. This approach enables the project to:

- Define a family of algorithms (exercise evaluation methods).
- Encapsulate each algorithm in its own class.
- Make algorithms interchangeable, allowing the system to adapt to new exercises without altering the existing codebase.

### Example Structure
1. **Abstract Class**: Defines a common interface for all exercises.
2. **Concrete Strategies**: Implements specific logic for each exercise (e.g., squats, push-ups, lunges).
3. **Context Class**: Selects and executes the appropriate strategy based on user input.

```python
class ExerciseStrategy:
    def evaluate(self, pose_data):
        raise NotImplementedError("Subclasses must implement this method")

class SquatStrategy(ExerciseStrategy):
    def evaluate(self, pose_data):
        # Logic for evaluating squats
        pass

class PushUpStrategy(ExerciseStrategy):
    def evaluate(self, pose_data):
        # Logic for evaluating push-ups
        pass

class ExerciseContext:
    def __init__(self, strategy):
        self.strategy = strategy

    def execute_strategy(self, pose_data):
        return self.strategy.evaluate(pose_data)
```

## Installation

### Prerequisites
- Python 3.8+
- Flask
- MediaPipe

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/ebubekirdgn/Pose-Detection-With-Flask
   cd Pose-Detection-With-Flask/fitness-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the app in your browser at `http://127.0.0.1:5000`.

## Usage
1. Launch the application.
2. Provide input via webcam or upload a video file.
3. Select the type of exercise you are performing.
4. Receive real-time feedback on your posture and form.

## Folder Structure
```
fitness-app/
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── exercises/
│   ├── exercise_strategy.py
│   ├── squat_strategy.py
│   └── pushup_strategy.py
├── app.py
├── requirements.txt
└── README.md
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
[EbubekirDogan] - [ebubekir.dogan@bil.omu.edu.tr]

Project Link: [https://github.com/ebubekirdgn/Pose-Detection-With-Flask](https://github.com/ebubekirdgn/Pose-Detection-With-Flask)

