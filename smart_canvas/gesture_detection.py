from threading import Thread
import time

import mediapipe as mp
import cv2

mpHands = mp.solutions.hands


class HandDetect:
    """
    Class that continuously gets finger count with a dedicated thread.
    """

    def __init__(self):
        self.hands = mpHands.Hands(
            max_num_hands=2, 
            min_detection_confidence=0.8, 
            min_tracking_confidence=0.8
        )

    def count_fingers(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        # hand landmark positions (x and y)
        handLandmarks = []

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Initially set finger count to 0 for each cap
        fingerCount = 0

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label

                # Fill list with x and y positions of each landmark
                for landmarks in hand_landmarks.landmark:
                    handLandmarks.append([landmarks.x, landmarks.y])

                if handLabel == "Left" and handLandmarks[4][0] > handLandmarks[3][0]:   # Left thumb
                    fingerCount = fingerCount+1
                elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:    # Right thumb
                    fingerCount = fingerCount+1

                # Other fingers: TIP y position must be lower than PIP y position, 
                #   as image origin is in the upper left corner.
                if handLandmarks[8][1] < handLandmarks[6][1]:       #Index finger
                    fingerCount = fingerCount+1
                if handLandmarks[12][1] < handLandmarks[10][1]:     #Middle finger
                    fingerCount = fingerCount+1
                if handLandmarks[16][1] < handLandmarks[14][1]:     #Ring finger
                    fingerCount = fingerCount+1
                if handLandmarks[20][1] < handLandmarks[18][1]:     #Pinky
                    fingerCount = fingerCount+1
            # Display finger count
            cv2.putText(frame, str(fingerCount), (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 10)
        return fingerCount
