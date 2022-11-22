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
        self.fingers_statuses = {}
        self.count = 0


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


    def check_thumbs_up(self, HandLabel, landmarks):
        #Check if thumb tip is higher than index tip
        if HandLabel == "Left" and landmarks[4][1] < landmarks[8][1]:   # Left thumb up
            self.fingers_statuses[landmarks[4][2].upper()+'_THUMB_UP'] = True
        
        if HandLabel == "Right" and landmarks[4][1] < landmarks[8][1]:    # Right thumb up
            self.fingers_statuses[landmarks[4][2].upper()+'_THUMB_UP'] = True
        
        #Check if thumb tip lower than wrist point
        if HandLabel == "Left" and landmarks[4][1] > landmarks[0][1]:   # Left thumb down
            self.fingers_statuses[landmarks[4][2].upper()+'_THUMB_DOWN'] = True
        
        if HandLabel == "Right" and landmarks[4][1] > landmarks[0][1]:    # Right thumb down
            self.fingers_statuses[landmarks[4][2].upper()+'_THUMB_DOWN'] = True


    def count_fingers(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        
        fingerCount = 0
        hand_gesture = {'RIGHT': "UNKNOWN", 'LEFT': "UNKNOWN"}

        # a dictionary to store the status (i.e., True for open and False for close) of each finger of both hands.
        self.fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                            'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                            'LEFT_RING': False, 'LEFT_PINKY': False, 'RIGHT_THUMB_UP': False, 'LEFT_THUMB_UP': False,
                            'RIGHT_THUMB_DOWN': False, 'LEFT_THUMB_DOWN': False}

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
                    self.fingers_statuses[handLandmarks[4][2].upper()+'_THUMB'] = True
                elif handLabel == "Right" and handLandmarks[4][0] < handLandmarks[3][0]:    # Right thumb
                    fingerCount = fingerCount+1
                    self.fingers_statuses[handLandmarks[4][2].upper()+'_THUMB'] = True

                self.check_thumbs_up(handLabel, handLandmarks)

                # Other fingers: TIP y position must be lower than PIP y position, 
                #   as image origin is in the upper left corner.
                if handLandmarks[8][1] < handLandmarks[6][1]:       #Index finger
                    fingerCount = fingerCount+1
                    self.fingers_statuses[handLandmarks[8][2].upper()+'_INDEX'] = True
                if handLandmarks[12][1] < handLandmarks[10][1]:     #Middle finger
                    fingerCount = fingerCount+1
                    self.fingers_statuses[handLandmarks[12][2].upper()+'_MIDDLE'] = True
                if handLandmarks[16][1] < handLandmarks[14][1]:     #Ring finger
                    fingerCount = fingerCount+1
                    self.fingers_statuses[handLandmarks[16][2].upper()+'_RING'] = True
                if handLandmarks[20][1] < handLandmarks[18][1]:     #Pinky
                    fingerCount = fingerCount+1
                    self.fingers_statuses[handLandmarks[20][2].upper()+'_PINKY'] = True

            self.count = fingerCount
            hand_gesture = self.recognizeGesture(hand_gesture)
        
        return fingerCount, hand_gesture
    

    def recognizeGesture(self, hands_gestures):
        hands_labels = {'RIGHT', 'LEFT'}
        
        # Iterate over the left and right hand.
        for hand_index, hand_label in enumerate(hands_labels):  
            # Check if the person is making the 'V' gesture with the hand.
            if self.count == 2  and self.fingers_statuses[hand_label+'_MIDDLE'] and self.fingers_statuses[hand_label+'_INDEX']:
                # Update the gesture value of the hand that we are iterating upon to V SIGN.
                hands_gestures[hand_label] = "V SIGN"
            # Check if the person is making the 'SPIDERMAN' gesture with the hand.
            elif self.count == 3 and self.fingers_statuses[hand_label+'_THUMB'] and self.fingers_statuses[hand_label+'_INDEX'] and self.fingers_statuses[hand_label+'_PINKY']:  
                hands_gestures[hand_label] = "SPIDERMAN SIGN"
            #Check if person is doing thumbs up
            elif self.fingers_statuses[hand_label+'_THUMB_UP']:
                hands_gestures[hand_label] = "THUMBS UP"
            #Check if person is doing thumbs down
            elif self.fingers_statuses[hand_label+'_THUMB_DOWN']:  
               hands_gestures[hand_label] = "THUMBS DOWN"

        return hands_gestures