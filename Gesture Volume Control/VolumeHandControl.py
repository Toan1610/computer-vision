import cv2
import mediapipe as mp
import math
import pulsectl

# Khởi tạo Mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Kết nối PulseAudio để điều khiển âm lượng
pulse = pulsectl.Pulse('volume-control')
sinks = pulse.sink_list()
default_sink = sinks[0]   # loa mặc định

# Mở camera
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    # Chuyển sang RGB cho Mediapipe
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            h, w, c = img.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

            # Nếu phát hiện điểm 4 (ngón cái) và 8 (ngón trỏ)
            if lmList:
                x1, y1 = lmList[4][1], lmList[4][2]   # ngón cái
                x2, y2 = lmList[8][1], lmList[8][2]   # ngón trỏ

                # Tính khoảng cách
                length = math.hypot(x2 - x1, y2 - y1)

                # Map khoảng cách 20 - 200 pixel -> volume 0.0 - 1.0
                vol = min(max((length - 20) / 180, 0.0), 1.0)
                pulse.volume_set_all_chans(default_sink, vol)

                # Vẽ trực quan
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # Hiển thị phần trăm
                cv2.putText(img, f'Vol: {int(vol*100)}%', (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Hand Volume Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
