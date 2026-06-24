# Sign Language to Speech Converter

A real-time Sign Language Recognition system that detects sign language gestures through a webcam and converts them into spoken words. The project uses MediaPipe for landmark extraction and XGBoost for gesture classification.

## Features

* Real-time sign language recognition using a webcam
* Hand and pose landmark extraction with MediaPipe
* XGBoost-based classification model
* Speech output using Windows Speech API
* Confidence-based prediction filtering
* Support for multiple sign classes

## Tech Stack

* Python
* OpenCV
* MediaPipe
* XGBoost
* Scikit-learn
* NumPy
* Pandas


## Model Performance

* Achieved **89.4% accuracy** on the initial 5-sign dataset
* Expanded to support 10 sign classes
* Real-time webcam inference with speech output

## Installation

```bash
git clone https://github.com/krishnasharma180/Sign_Language_Pedictor.git
cd Sign_Language_Predictor
```

## Usage

```bash
python src/main.py
```

* Press **S** to record a sign
* Press **Q** to quit the application

## Demo

![Demo](assets/demo.gif)

## Future Improvements

* Increase the number of supported signs
* Continuous sentence recognition
* LSTM/GRU-based sequence models
* Mobile and web deployment

## Dataset

This project was trained using the Kaggle ASL Signs dataset. The dataset is not included in this repository.
