import os
import threading
import yt_dlp
import cv2
import torch
import dotenv
import imutils
import fight_module

# Load .env file
dotenv.load_dotenv()

YOLO_MODEL  = os.getenv("YOLO_MODEL")
FIGHT_MODEL = os.getenv("FIGHT_MODEL")

# Get a direct stream URL from YouTube
def get_direct_video_url(youtube_url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict['url']

# For threaded‐safe display (if you ever use outputFrame)
outputFrame = None
lock = threading.Lock()

def detect(video_input):
    global outputFrame, lock

    FIGHT_ON = False
    FIGHT_ON_TIMEOUT = 5  # seconds

    fdet = fight_module.FightDetector(FIGHT_MODEL)
    yolo = fight_module.YoloPoseEstimation(YOLO_MODEL)

    # ─── iterate over every frame in the video/stream ─────────────────────────
    for result in yolo.estimate(video_input):
        # raw and annotated frames
        orig_frame   = result.orig_img
        result_frame = result.plot()

        # optional resize if too tall
        if result_frame.shape[0] > 720:
            result_frame = imutils.resize(result_frame, width=1280)

        try:
            boxes = result.boxes.xyxy.tolist()
            xyn   = result.keypoints.xyn.tolist()
            confs = [] if result.keypoints.conf is None else result.keypoints.conf.tolist()
            ids   = [] if result.boxes.id is None else [str(int(i)) for i in result.boxes.id]

            interaction_boxes = fight_module.get_interaction_box(boxes)

            for inter_box in interaction_boxes:
                x1, y1, x2, y2 = map(int, inter_box)
                # draw green interaction box
                cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                both_fighting = []
                for conf, kp, box in zip(confs, xyn, boxes):
                    cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
                    if x1 <= cx <= x2 and y1 <= cy <= y2:
                        both_fighting.append(fdet.detect(conf, kp))

                # if any person in the box is fighting
                if any(both_fighting):
                    FIGHT_ON = True

        except (TypeError, IndexError):
            pass

        # update the shared frame (if you display via another thread/UI)
        with lock:
            outputFrame = result_frame.copy()

        # draw fight alarm if on
        if FIGHT_ON:
            # reuse last inter_box for red rectangle/text
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(result_frame, "FIGHT DETECTED!", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            FIGHT_ON_TIMEOUT -= 0.1

        # reset after timeout
        if FIGHT_ON_TIMEOUT <= 0:
            FIGHT_ON = False
            FIGHT_ON_TIMEOUT = 5

        # show the result
        cv2.imshow("Fight Detection", result_frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    # extract a direct stream URL once, then pass that to detect()
    direct_url = get_direct_video_url("https://www.youtube.com/watch?v=99WjyvJDxng")
    detect(direct_url)
