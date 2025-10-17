import os
import cv2
import numpy as np
import pulsectl
from cvzone.HandTrackingModule import HandDetector

# =======================
# PulseAudio: chọn sink mặc định & hàm set volume
# =======================
pulse = pulsectl.Pulse('hand-volume-control')

def get_default_sink():
    try:
        default_name = pulse.server_info().default_sink_name
        for s in pulse.sink_list():
            if s.name == default_name:
                return s 
        # fallback: lấy sink đầu nếu không match tên
        return pulse.sink_list()[0]
    except Exception:
        # cuối cùng vẫn cố gắng lấy phần tử đầu
        return pulse.sink_list()[0]

default_sink = get_default_sink()

def set_volume_linux(percent: int):
    """percent: 0..100"""
    percent = int(max(0, min(100, percent)))
    pulse.volume_set_all_chans(default_sink, percent/100.0)

# =======================
# Camera & HandDetector
# =======================
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

detector = HandDetector(detectionCon=0.7, maxHands=1)

# =======================
# Load ảnh overlay 0..5
# =======================
FOLDER = "FingerImages"
os.makedirs(FOLDER, exist_ok=True)

def ensure_overlay_exists(idx: int):
    """Nếu thiếu ảnh, tự tạo ảnh số trắng đen 200x200."""
    path = os.path.join(FOLDER, f"{idx}.png")
    if not os.path.isfile(path):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.putText(img, str(idx), (65, 140), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 8, cv2.LINE_AA)
        cv2.imwrite(path, img)
    return path

overlayList = []
for i in range(0, 6):  # 0..5
    p = ensure_overlay_exists(i)
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    overlayList.append(im)

def to_rgba(img_bgr_or_bgra):
    """Đảm bảo overlay có 4 kênh (RGBA)."""
    if img_bgr_or_bgra is None:
        return None
    if img_bgr_or_bgra.shape[2] == 4:
        return img_bgr_or_bgra
    bgr = img_bgr_or_bgra
    alpha = np.full((bgr.shape[0], bgr.shape[1], 1), 255, dtype=np.uint8)
    return np.concatenate([bgr, alpha], axis=2)

overlayList = [to_rgba(im) for im in overlayList]

def overlay_transparent(bg, overlay_rgba, x, y, scale=1.0):
    """Dán overlay RGBA lên bg BGR tại (x,y) với scale; auto cắt cho vừa khung."""
    if overlay_rgba is None or overlay_rgba.size == 0:
        return bg
    oh, ow = overlay_rgba.shape[:2]
    new_w, new_h = max(1, int(ow * scale)), max(1, int(oh * scale))
    overlay = cv2.resize(overlay_rgba, (new_w, new_h), interpolation=cv2.INTER_AREA)

    h, w = bg.shape[:2]
    if x >= w or y >= h:
        return bg

    # cắt nếu tràn
    overlay = overlay[:max(0, h - y), :max(0, w - x)]
    if overlay.size == 0:
        return bg

    b, g, r, a = cv2.split(overlay)
    alpha = a.astype(float) / 255.0
    alpha = cv2.merge([alpha, alpha, alpha])

    roi = bg[y:y+overlay.shape[0], x:x+overlay.shape[1]].astype(float)
    overlay_rgb = cv2.merge([b, g, r]).astype(float)

    blended = alpha * overlay_rgb + (1 - alpha) * roi
    bg[y:y+overlay.shape[0], x:x+overlay.shape[1]] = blended.astype(np.uint8)
    return bg

# =======================
# Main loop
# =======================
while True:
    ok, img = cap.read()
    if not ok:
        break

    hands, img = detector.findHands(img, flipType=False)

    totalFingers = 0
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)  # list 5 phần tử 0/1
        totalFingers = int(sum(fingers))    # 0..5

        # Map 0..5 -> 0..100 (%)
        vol_percent = int(np.interp(totalFingers, [0, 5], [0, 100]))
        set_volume_linux(vol_percent)

        # Hiển thị số
        cv2.putText(img, f'Fingers: {totalFingers}  Vol: {vol_percent}%',
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # Chèn overlay (resize tự động, ~35% chiều cao khung)
        hCam, wCam = img.shape[:2]
        overlay = overlayList[totalFingers]
        target_h = int(0.35 * hCam)
        scale = target_h / max(1, overlay.shape[0])
        img = overlay_transparent(img, overlay, 10, 60, scale=scale)

    cv2.imshow("Hand Volume Control (Linux + pulsectl)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
