import mediapipe as mp
import cv2
import math
import numpy as np

#Initializations: static code
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils



class HandDetector:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.hands = mpHands.Hands(max_num_hands=max_num_hands, min_detection_confidence=min_detection_confidence,
                                   min_tracking_confidence=min_tracking_confidence)


    def findHandLandMarks(self, image, handNumber=0, draw=False):
        originalImage = image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # mediapipe needs RGB
        results = self.hands.process(image)
        landMarkList = []

        if results.multi_handedness:

            label = results.multi_handedness[handNumber].classification[0].label  # label gives if hand is left or right
            #print(label)
            #account for inversion in webcams
            if label == "Left":
                label = "Right"
            elif label == "Right":
                label = "Left"


        if results.multi_hand_landmarks:  # returns None if hand is not found
            hand = results.multi_hand_landmarks[handNumber] #results.multi_hand_landmarks returns landMarks for all the hands


            for id, landMark in enumerate(hand.landmark):
                # landMark holds x,y,z ratios of single landmark
                imgH, imgW, imgC = originalImage.shape  # height, width, channel for image
                xPos, yPos = int(landMark.x * imgW), int(landMark.y * imgH)
                landMarkList.append([id, xPos, yPos, label])

            if draw:
                mpDraw.draw_landmarks(originalImage, hand, mpHands.HAND_CONNECTIONS)

        return landMarkList




handDetector = HandDetector(min_detection_confidence=0.7,max_num_hands=2)
webcamFeed = cv2.VideoCapture(0)


while True:
    status, image = webcamFeed.read()
    handLandmarks = handDetector.findHandLandMarks(image=image, draw=True)
    count=0

    if(len(handLandmarks) != 0):


        if handLandmarks[4][3] == "Right" and handLandmarks[4][1] > handLandmarks[3][1]:       #Right Thumb
            count = count+1
        elif handLandmarks[4][3] == "Left" and handLandmarks[4][1] < handLandmarks[3][1]:       #Left Thumb
            count = count+1
        if handLandmarks[8][2] < handLandmarks[6][2]:       #Index finger
            count = count+1
        if handLandmarks[12][2] < handLandmarks[10][2]:     #Middle finger
            count = count+1
        if handLandmarks[16][2] < handLandmarks[14][2]:     #Ring finger
            count = count+1
        if handLandmarks[20][2] < handLandmarks[18][2]:     #Little finger
            count = count+1
        if count ==1:
            cv2.putText(image, "First filter", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)

        if count == 2:
            cv2.putText(image, "Second filter", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        if count ==3:
            cv2.putText(image, "Third filter", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        if count ==4:
            cv2.putText(image, "Fourth filter", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        if count ==5:
            cv2.putText(image, "Take Picture", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)


    #cv2.putText(image, str(count), (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 25)
    cv2.imshow("Volume", image)
    cv2.waitKey(1)
    #def outputreturn(self, count=count):
         #return(count)
