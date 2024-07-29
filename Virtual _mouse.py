import cv2
import mediapipe as mp
import pyautogui
from math import hypot

# Initialize MediaPipe Hands and PyAutoGUI
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Screen size
screen_width, screen_height = pyautogui.size()

# Initialize video capture
cap = cv2.VideoCapture(0)

# Speed multiplier for cursor movement
speed_multiplier = 2.0  # Adjust this value to increase or decrease speed

def find_finger_tips_and_bases(hand_landmarks, w, h):
    """Extracts thumb tip, index tip, and base points from hand landmarks."""
    landmarks = {id: (int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(hand_landmarks.landmark)}
    return (landmarks[4], landmarks[8]), (landmarks[17], landmarks[20])  # Thumb and Index tips, Pinky Base and Tip

# Variables to store the previous cursor position
prev_x, prev_y = None, None

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    h, w, _ = img.shape  # Get image dimensions

    if results.multi_hand_landmarks:
        hands_landmarks = results.multi_hand_landmarks

        if len(hands_landmarks) >= 2:
            # Assuming the right hand is the first detected hand
            right_hand = hands_landmarks[0]
            (thumb1, index1), _ = find_finger_tips_and_bases(right_hand, w, h)
            x1, y1 = thumb1
            x2, y2 = index1

            # Assuming the left hand is the second detected hand
            left_hand = hands_landmarks[1]
            (_, _), (pinky_base2, pinky_tip2) = find_finger_tips_and_bases(left_hand, w, h)
            x3, y3 = pinky_base2
            x4, y4 = pinky_tip2

            # Draw landmarks and connections
            mpDraw.draw_landmarks(img, right_hand, mpHands.HAND_CONNECTIONS)
            mpDraw.draw_landmarks(img, left_hand, mpHands.HAND_CONNECTIONS)

            # Calculate movement deltas
            if prev_x is not None and prev_y is not None:
                delta_x = (x2 - prev_x) * speed_multiplier
                delta_y = (y2 - prev_y) * speed_multiplier
            else:
                delta_x = delta_y = 0

            # Update previous position
            prev_x, prev_y = x2, y2

            # Move mouse with the right hand
            screen_x = int(screen_width * (x2 / w))
            screen_y = int(screen_height * ((h - y2) / h))  # Invert y-axis
            pyautogui.moveTo(screen_x, screen_y)  # Move cursor to the position

            # Visual feedback for cursor
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)

            # Click with the left hand
            distance = hypot(x4 - x3, y4 - y3)
            if distance < 30:  # Adjust this threshold as needed
                pyautogui.click()
                cv2.circle(img, (x4, y4), 10, (255, 0, 0), cv2.FILLED)

    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
