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

    def findHandLandMarks(self, hand_landmark, label):

        # label gives if hand is left or right
        # account for inversion in webcams
        if label == "Left":
            label = "Right"
        elif label == "Right":
            label = "Left"

        landMarkList = []

        # Fill list with x and y positions of each landmark
        for landmarks in hand_landmark.landmark:
            landMarkList.append([landmarks.x, landmarks.y, label])

        return landMarkList

    def count_fingers(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        fingerCount = 0

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label
                # hand landmark positions (x, y, label)
                handLandmarks = self.findHandLandMarks(hand_landmarks, handLabel)

                #For thumbs we check the thumb TIP is over the thumb IP x
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
            
        return fingerCount
