import cv2
import mediapipe as mp
import numpy as np
import joblib
from collections import deque, Counter
import time
import win32com.client
import threading

last_spoken_time = 0

last_spoken = ""
prediction_history = deque(maxlen=5)

model = joblib.load("C:\\Users\\Krishna\\OneDrive\\Desktop\\Sigh_Language_Predictor\\models\\sign_xgb2.pkl")
le=joblib.load("C:\\Users\\Krishna\\OneDrive\\Desktop\\Sigh_Language_Predictor\\models\\label_encoder2.pkl")


def speak(text):
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Speak(text)
    
    
def sequence_to_features(sequence):

    sequence = np.array(sequence)

    features = []

    for col in range(sequence.shape[1]):
        vals = sequence[:, col]

        features.extend([
        np.mean(vals),
        np.std(vals),
        np.min(vals),
        np.max(vals),
        vals[0],
        vals[-1],
        vals[-1] - vals[0]
    ])

    return np.array(features)


mp_holistic = mp.solutions.holistic
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prediction_text = "Press S to Record"
confidence_text = ""

with mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as holistic:

    sequence = []
    recording = False

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = holistic.process(rgb)

        frame_features = np.zeros(225)

        # LEFT HAND
        if results.left_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS
            )

            for i, lm in enumerate(results.left_hand_landmarks.landmark):

                frame_features[i*3+0] = lm.x
                frame_features[i*3+1] = lm.y
                frame_features[i*3+2] = lm.z


        # RIGHT HAND
        if results.right_hand_landmarks:

            offset = 63

            mp_draw.draw_landmarks(
                frame,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS
            )

            for i, lm in enumerate(results.right_hand_landmarks.landmark):

                frame_features[offset+i*3 + 0]=lm.x
                frame_features[offset+i*3 + 1]=lm.y
                frame_features[offset + i*3 + 2]=lm.z


        # POSE
        if results.pose_landmarks:

            offset = 126

            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS
            )

            for i, lm in enumerate(results.pose_landmarks.landmark[:33]):

                frame_features[offset+i*3 + 0] = lm.x
                frame_features[offset+i*3 + 1] = lm.y
                frame_features[offset+i*3 + 2] = lm.z

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):

            sequence = []
            recording = True
            last_spoken=""

            prediction_text = "Recording..."
            confidence_text = ""

        if recording:

            sequence.append(frame_features)

            if len(sequence) >= 30:

                recording = False

                feature_vector = sequence_to_features(sequence)
                probs = model.predict_proba(
                    feature_vector.reshape(1, -1)
                )[0]

                idx = np.argmax(probs)

                prediction_num = model.classes_[idx]

                prediction = le.inverse_transform(
                    [prediction_num]
                )[0]
                confidence = probs[idx] * 100

                if confidence > 40:

                    prediction_history.append(prediction)

                    stable_prediction = Counter(
                        prediction_history
                    ).most_common(1)[0][0]

                    prediction_text = f"Prediction: {stable_prediction}"
                    confidence_text = f"Confidence: {confidence:.1f}%"
                    if (
                        stable_prediction != last_spoken
                        and time.time() - last_spoken_time > 2
                        ):
                        print("Speaking:", stable_prediction)
                        threading.Thread(
                            target=speak,
                            args=(stable_prediction,),
                            daemon=True
                        ).start()
                        last_spoken = stable_prediction
                        last_spoken_time=time.time()
                    prediction_history.clear() 

                else:

                    prediction_text = "Prediction: Unknown"
                    confidence_text = f"Confidence: {confidence:.1f}%"
                    prediction_history.clear() 

        cv2.putText(
            frame,
            prediction_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            confidence_text,
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        cv2.imshow("Sign Language Recognition", frame)

        if key == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()