from importlib.resources import files

import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-attendance-ccf86-default-rtdb.firebaseio.com/" ,
    'storageBucket':"face-attendance-ccf86.appspot.com"
})


folderPath = 'images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
for path in pathList:
    #taking mages
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

    #immediately after taking images sending it to database
  #  print(path)
   # print(os.path.splitext(path)[0])  # to remove .png from image path to show only name
print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # change bgr to rgb, as opencv uses bgr and face re  lib uses rgb
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("encoding start")

encodeListKnown = findEncodings(imgList)
encodeListKnownwithIds = [encodeListKnown,studentIds]
print("encoding complete")

file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownwithIds,file)
file.close()
print("file saved")

