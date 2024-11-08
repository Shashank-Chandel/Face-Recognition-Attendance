import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.db import reference

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-attendance-ccf86-default-rtdb.firebaseio.com/"
})

ref = db.reference('students')

data = {
    "nick":
        {
            "name": "Nick Fury",
            "course": "B.TECH",
            "year": "3rd Year",
            "Total_Attendance": 5,
            "last_attendance_time": "12-11-2024  09:00:00" ,
            "roll_no": 1
        } ,
    "tony":
        {
            "name": "Tony Stark",
            "course": "B.TECH",
            "year": "3rd Year",
            "Total_Attendance": 1,
            "last_attendance_time": "12-11-2024  09:01:00",
            "roll_no": 2
        }

}

for key,value in data.items():
    ref.child(key).set(value)
