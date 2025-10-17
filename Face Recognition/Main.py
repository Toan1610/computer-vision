import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
from supabase import create_client, Client
from datetime import datetime

# ==============================
# Kết nối Supabase
# ==============================
url = "https://hguejnrbvmwkdnezvqzk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhndWVqbnJidm13a2RuZXp2cXprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTMzOTkyNywiZXhwIjoyMDY2OTE1OTI3fQ.Vip7dj1vGNpV2VcwVuGYMrW5cG5q2DQmXp-ykb-Ixl8"
supabase: Client = create_client(url, key)

# ==============================
# Webcam & Background
# ==============================
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

DISPLAY_FRAMES = 120

imgBackground = cv2.imread('Face Recognition/Files/Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Face Recognition/Files/Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# ==============================
# Load Encode File
# ==============================
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

# ==============================
# Variables
# ==============================
modeType = 0
counter = 0
id = -1
imgStudent = []
studentInfo = None

# ==============================
# Main Loop
# ==============================
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # ==============================
                # Get Data from Supabase Students table
                # ==============================
                response = supabase.table("Students").select("*").eq("id", id).execute()
                studentInfo = response.data[0] if response.data else None
                print(studentInfo)

                # ==============================
                # Get Image from Supabase Storage
                # ==============================
                try:
                    res = supabase.storage.from_("student-images").download(f"Images/{id}.png")
                    array = np.frombuffer(res, np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                except Exception as e:
                    print("Error fetching image:", e)
                    imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)

                # ==============================
                # Update Attendance
                # ==============================
                if studentInfo:
                    try:
                        # parse ISO string từ supabase
                        datetimeObject = datetime.fromisoformat(studentInfo['last_attendance_time'])
                    except Exception:
                        datetimeObject = datetime(2000, 1, 1)  # fallback nếu null/lỗi

                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print("Seconds since last attendance:", secondsElapsed)

                    if secondsElapsed > 30:
                        new_total = studentInfo['total_attendance'] + 1

                        # Insert vào bảng attendance
                        supabase.table("attendance").insert({
                            "student_id": id,
                            "status": "present",
                            "created_at": datetime.now().isoformat()
                        }).execute()

                        # Update bảng Students
                        supabase.table("Students").update({
                            "total_attendance": new_total,
                            "last_attendance_time": datetime.now().isoformat()
                        }).eq("id", id).execute()
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10 and studentInfo:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    if imgStudent is not None and imgStudent.size > 0:
                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= DISPLAY_FRAMES:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
