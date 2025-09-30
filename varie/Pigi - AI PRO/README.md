# AI_PRO Project

## Overview

The AI_PRO project is a comprehensive system designed to recognize and count repetitions of various exercises using machine learning techniques. The project leverages MediaPipe for pose detection and a pre-trained SVM model for exercise classification. The system is built using Flask for the web interface and streaming capabilities.

## Project Structure

The project is organized into several modules, each responsible for different functionalities:

- `app.py`: The main entry point for the Flask application.
- `utils/`: Contains utility modules for various functionalities.
  - `global_vars.py`: Defines and initializes global variables used across the project.
  - `video_stream.py`: Handles video streaming and exercise recognition.
  - `exercise_count.py`: Contains functions for counting repetitions of different exercises.
  - `routes.py`: Defines the routes for the Flask application.
  - `draw.py`: Contains functions for drawing landmarks and other visual elements on the video frames.
  - `config.py`: Contains configuration settings for the Flask application and Keycloak integration.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mazzoccajr/AI_PRO.git
   cd AI_PRO
   ```

2. Create a virtual environment and activate it:
   ```bash
   conda create -n aipro_env python=3.10
   conda activate aipro_env
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the file run.bat

## User Credentials

### User
- **Username:** supermario
- **Password:** mario

### Administrator
- **Username:** superluigi
- **Password:** luigi

## Key Features

- **Exercise Recognition**: Uses MediaPipe for pose detection and an SVM model for exercise classification.
- **Repetition Counting**: Counts repetitions for exercises like squats, pushups, and military press.
- **Rest Timer**: Implements a rest timer between sets.
- **Video Streaming**: Streams video from the webcam with overlaid exercise information.
- **User Authentication**: Integrates with Keycloak for user authentication and role-based access control.

## Other Modules

- `ML/`: Contains machine learning modules for training and testing.
  - `dataset/`: Contains Datasets.
      - `DatiGenerati/`: Dataset of automatically generated data.
      - `DatiReali/`: Dataset of data collected from the webcam.
  - `pkl/`: Contains machine learning models.
      - `datigenerati/`: Model trained with automatically generated data.
      - `datireali/`: Model trained with data collected from the webcam.
- `keycloak-26.1.0/`: Contains utility modules to run the Keycloak server.
- `video/`: Contains videos of correct executions.
- `logs/`: Contains server logs.



## Authors

- Giuseppe Mazzocca
- Angelo Andrea Nozzolillo
- Pierluigi Montieri
