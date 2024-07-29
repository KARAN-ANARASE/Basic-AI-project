import cv2 
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np 

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands 
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volMin, volMax = volume.GetVolumeRange()[:2]
preset_vol = -20.0  # Volume level to set when touching

def get_finger_tip_and_base(hand_landmarks, w, h):
    """Extracts thumb and index finger tips and base points from hand landmarks."""
    landmarks = {id: (int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(hand_landmarks.landmark)}
    return (landmarks[4], landmarks[8], landmarks[17], landmarks[20])  # Thumb, Index, Pinky Base, Pinky Tip

volume_set = False

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    h, w, _ = img.shape  # Define width and height here

    lmList = []
    if results.multi_hand_landmarks:
        hands_landmarks = []
        for hand_landmark in results.multi_hand_landmarks:
            lmList.append(hand_landmark)
            hands_landmarks.append(hand_landmark)
            mpDraw.draw_landmarks(img, hand_landmark, mpHands.HAND_CONNECTIONS)
    
    if len(lmList) >= 2:
        # Use the first hand for volume control
        hand1 = lmList[0]
        thumb1, index1, _, _ = get_finger_tip_and_base(hand1, w, h)
        x1, y1 = thumb1
        x2, y2 = index1

        # Use the second hand for setting the volume
        hand2 = lmList[1]
        thumb2, index2, _, _ = get_finger_tip_and_base(hand2, w, h)
        x3, y3 = thumb2
        x4, y4 = index2

        # Control volume with the first hand
        cv2.circle(img, (x1, y1), 4, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 4, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

        length = hypot(x2 - x1, y2 - y1)
        if not volume_set:
            vol = np.interp(length, [15, 220], [volMin, volMax])
            volume.SetMasterVolumeLevel(vol, None)

        # Check if the second hand's index finger touches the thumb
        distance = hypot(x4 - x3, y4 - y3)
        if distance < 30:  # Adjust this threshold as needed
            volume_set = True
            volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel(), None)
        else:
            volume_set = False

        # Draw circles for the second hand
        cv2.circle(img, (x3, y3), 4, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x4, y4), 4, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x3, y3), (x4, y4), (0, 255, 0), 3)

    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
