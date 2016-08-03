import time
from datetime import datetime
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imutils
from PIL import Image
import cv2
import os
import openface
from multiprocessing import Process

# directories
fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '../..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))

class VideoCamera(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""

    def __init__(self):
        #self.cam = WebcamVideoStream(src=0).start() # 0 = lifecam, 1 = iSight
        self.fps = FPS().start()
        self.cam = cv2.VideoCapture(0) 	
        self.cam.set(cv2.cv.CV_CAP_PROP_CONVERT_RGB, False);
        self.cam.set(cv2.cv.CV_CAP_PROP_FPS, 60);
        self.frame = None
        self.bb = None
        self.cam.set(3, 320)
        self.cam.set(4, 240)
        #self.faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        #time.sleep(1)

    def get_bounding_box(self, hasMultiple=None, username=None):
        # openface face detection
        rgbImg = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if hasMultiple is not None and hasMultiple is True:
            bbs = align.getAllFaceBoundingBoxes(rgbImg)
        else:
            bb = align.getLargestFaceBoundingBox(rgbImg, skipMulti=True)
            bbs = [bb]

        for bb in bbs:
            if bb is not None:
                bl = (bb.left(), bb.bottom())
                tr = (bb.right(), bb.top())
                cv2.rectangle(self.frame, bl, tr, (0, 255, 0), 1)	
                landmarks = align.findLandmarks(rgbImg, bb)
                alignedFace = align.align(96, rgbImg, bb,
                                            landmarks=landmarks,
                                            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)

                crop_img = rgbImg[bb.top():(bb.top() + bb.height()), bb.left():(bb.left() + bb.width())] # Crop from x, y, w, h -> 100, 200, 300, 400
                # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]

                font = cv2.FONT_HERSHEY_SIMPLEX
                line_type = cv2.CV_AA
                cv2.putText(self.frame, 'AP Origin', (bb.left(), bb.top() - 10), font, 0.6, (255, 255, 255), 1, line_type)

                if crop_img.size > 0: 
                    if username is not None:
                        t = datetime.now()
                        #cv2.imshow('cropped', crop_img)
                        #cv2.imshow(t.strftime('%Y-%m-%d %H:%M:%S'), crop_img)
                        formatted_t = t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        directory = ("./app/training/%s/" % (username))
                        crop_img_file_name = ("%s%s.jpg" % (directory, formatted_t))

                        # write cropped image to training folder
                        #cv2.imwrite(crop_img_file_name, crop_img)
                        saved_img = Image.fromarray(crop_img)
                        saved_img.save(crop_img_file_name)
                        print crop_img_file_name
            # end of openface face detection

    def process_frame(self):
        bb = None
        bb_process = Process(target=self.get_bounding_box)
        bb_process.start()
        bb_process.join()

    def get_frame(self, hasMultiple=None, username=None):
        ret, self.frame = self.cam.read()
        self.frame = cv2.flip(self.frame, 1)
        #frame = self.cam.read()

        # resized for speed 
        # width=320:20fps, 480:11fps, 640:6fps
        #self.frame = imutils.resize(self.frame, width=640)
        self.get_bounding_box(hasMultiple, username)

        ret3, jpeg = cv2.imencode('.jpg', self.frame)
        self.fps.update()

        return jpeg.tobytes()

    def __del__(self):
        #self.cam.stop()
        self.cam.release()
        cv2.destroyAllWindows()
        self.fps.stop()
        print "[INFO] approx. FPS: {:.2f}".format(self.fps.fps())