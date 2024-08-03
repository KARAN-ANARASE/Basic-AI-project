import cv2
import mediapipe as mp
import numpy as np

# Function to detect the middle finger gesture
def is_middle_finger_extended(landmarks):
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
    middle_base = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y
    
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y

    if (middle_tip < middle_base and
        index_tip > middle_tip and
        ring_tip > middle_tip and
        pinky_tip > middle_tip and
        thumb_tip > middle_tip):
        return True
    return False

# Display warning message function
def display_warning_message():
    warning_message = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(warning_message, 'WARNING: Offensive Gesture', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Warning', warning_message)
    cv2.waitKey(2000)  # Display for 2 seconds
    cv2.destroyAllWindows()

# Display block message function
def display_block_message():
    block_message = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(block_message, 'You are BLOCKED', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4, cv2.LINE_AA)
    cv2.imshow('Blocked', block_message)
    cv2.waitKey(3000)  # Display for 3 seconds
    cv2.destroyAllWindows()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
offense_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            if is_middle_finger_extended(hand_landmarks):
                offense_count += 1
                if offense_count < 3:
                    display_warning_message()
                else:
                    display_block_message()
                    break

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or offense_count >= 4:
        break

cap.release()
cv2.destroyAllWindows()
