import os, cv2

ds = "dataset"  # folder containing your videos
exts = ('.mp4','.avi','.mov','.mkv','.flv','.wmv')

for f in os.listdir(ds):
    if f.lower().endswith(exts):
        vid_path = os.path.join(ds, f)
        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        out_dir = os.path.join(ds, os.path.splitext(f)[0] + "_frames")
        os.makedirs(out_dir, exist_ok=True)
        
        t = 0
        idx = 0
        while t < duration:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imwrite(os.path.join(out_dir, f"frame_{idx:04d}.jpg"), frame)
            idx += 1
            t += 1 / 3
        cap.release()