import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import os
#from EncodeGenerator import encodeListKnownwithIds, encodeListKnown, studentIds
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

#from EncodeGenerator import bucket

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
     'databaseURL':"https://face-attendance-ccf86-default-rtdb.firebaseio.com/" ,
     'storageBucket':"face-attendance-ccf86.appspot.com"
})

bucket = storage.bucket()
#from EncodeGenerator import encodeListKnownwithIds, encodeListKnown, studentIds

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('resoures/r1.png')

#inserting a mode images into a path
folderModePath = 'resoures/Modes'
modePathList = os.listdir(folderModePath) #give names of img
imgModeList = [] #list contains images
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))



#print(len(imgModeList))

#print(modePathList)

# load the encoding file
file = open('EncodeFile.p', 'rb')
encodeListKnownwithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownwithIds
#print(studentIds)

modeType = 0
counter = 0 #because we just want to show the downloaded data from DB only once so this will stop to download data again and


id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
       # print("matches",matches)
        #print("faceDis",faceDis)

        matchIndex = np.argmin(faceDis)
        #print("Match Index", matchIndex)

        if matches[matchIndex]:
            #print("Known Face Detected")
            #print(studentIds[matchIndex])
            y1 , x2 , y2 , x1 = faceLoc
            y1, x2, y2, x1 = y1*4 , x2*4 , y2*4 , x1*4
            bbox = 55 + x1, 162 + y1, x2-x1 , y2-y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]

            if counter == 0:
                counter = 1
                modeType = 1


    if counter != 0:

        if counter == 1:
            #get the data from the DB
            studentInfo = db.reference(f'students/{id}').get()
            print(studentInfo)
            # get the image from DB storage
            blob = bucket.get_blob(f'images/{id}.jpg')
            array = np.frombuffer(blob.download_as_string(),np.uint8)
            imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
            #update the data of attendance
          #  datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
           #                                    "%d-%m-%Y %H:%M:%S")
            #secondsElaspsed=(datetime.now()-datetimeObject).total_seconds()
            #print(secondsElaspsed)
            #if secondsElaspsed>30:
            ref = db.reference(f'students/{id}')
            studentInfo['Total_Attendance'] +=1
            ref.child('Total_Attendance').set(studentInfo['Total_Attendance'])
                #ref.child('last_attendance_time').set(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

        if 30<counter<50:
            modeType=2
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if counter<=30: #for first 5 frames just keep modeType = 1

            cv2.putText(imgBackground,str(studentInfo['Total_Attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,
                    (255,255,255),1)
            #cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
            #           (100, 100, 100), 2)
            cv2.putText(imgBackground, str(studentInfo['course']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                    (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['roll_no']), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                    (255, 255, 255), 1)

            #locn on screen      Font                 font size        font color          thickness
            # code to center name
            (w,h),_ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1 ,1)
            offset = (414-w)//2
            cv2.putText(imgBackground, str(studentInfo['name']),(808+offset,445),
                              cv2.FONT_HERSHEY_COMPLEX ,1 ,(50,50,50),2)

            imgBackground[175:175+216,909:909+216] = imgStudent
        counter+=1

        if counter>=50:
            counter=0
            modeType=0
            studentInfo=[]
            imgStudent=[]
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


    cv2.imshow("face attendance" , imgBackground)
    #cv2.imshow("Webcam" , img)
    cv2.waitKey(1)