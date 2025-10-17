import cv2
import face_recognition
import pickle
import os
from supabaseClient import supabase
import base64

# Thư mục chứa ảnh local
folderPath = 'Face Recognition/Files/Images'
pathList = os.listdir(folderPath)
print("Danh sách ảnh:", pathList)

imgList = []
studentIds = []

bucket_name = "student-images"

for path in pathList:
    fileName = os.path.join(folderPath, path)   # đường dẫn local đầy đủ
    storage_path = f"Images/{path}"             # đường dẫn trong bucket
    
    # Upload ảnh lên Supabase
    with open(fileName, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(
            storage_path,
            f,
            {"upsert": "true"}   # phải là string
        )
        print("Upload result:", res)

    # Đọc ảnh để encode gương mặt
    img = cv2.imread(fileName)
    imgList.append(img)

    # Lấy studentId từ tên file (giả sử tên file = ID.jpg)
    studentId = os.path.splitext(path)[0]
    studentIds.append(studentId)

    # Encode đường dẫn để public (nếu cần)
    encoded_path = base64.urlsafe_b64encode(storage_path.encode()).decode()
    print("Encoded path:", encoded_path)


# Hàm encode gương mặt
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:   # tránh lỗi nếu không nhận diện được mặt
            encodeList.append(encodings[0])
        else:
            print("Không tìm thấy gương mặt trong ảnh")
            encodeList.append(None)
    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# Lưu file encode
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("File Saved")
