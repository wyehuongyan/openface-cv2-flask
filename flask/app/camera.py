import time
from datetime import datetime
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from trainer import Trainer
import imutils
from PIL import Image
import numpy as np
import cv2
import os
import openface
import imagehash
from app import db
from app.models import Face, User

# directories
fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '../..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), imgDim=96,
                              cuda=False)               

class VideoCamera(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""

    # static class object
    trainer = Trainer()

    def __init__(self):
        #self.cam = WebcamVideoStream(src=0).start() # 0 = lifecam, 1 = iSight
        self.fps = FPS().start()
        self.cam = cv2.VideoCapture(0) 	
        self.frame = None
        self.bb = None
        self.cam.set(3, 480) # 480p resolution: 480x360
        self.cam.set(4, 360)
        self.id = None
        self.images = VideoCamera.trainer.retrieveFaceImage(None) # images dictionary

        print "VideoCamera instantiated"

    ##########################
    ##### Face Detection #####
    ##########################
    def get_bounding_box(self, hasMultiple=None, id=None):
        # openface face detection
        rgbImg = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.id = id

        if hasMultiple is not None and hasMultiple is True:
            bbs = align.getAllFaceBoundingBoxes(rgbImg)
        else:
            bb = align.getLargestFaceBoundingBox(rgbImg, skipMulti=True)
            bbs = [bb]

        for bb in bbs:
            if bb is not None:
                # draw bounding box
                bl = (bb.left(), bb.bottom())
                tr = (bb.right(), bb.top())
                cv2.rectangle(self.frame, bl, tr, (0, 255, 0), 1)	

                crop_img = rgbImg[bb.top():(bb.top() + bb.height()), bb.left():(bb.left() + bb.width())] # Crop from x, y, w, h -> 100, 200, 300, 400
                # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]

                # saving cropped image
                if crop_img.size > 0: 
                    t = datetime.now()
                    #cv2.imshow('cropped', crop_img)
                    #cv2.imshow(t.strftime('%Y-%m-%d %H:%M:%S'), crop_img)
                    formatted_t = t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    directory = ("./app/training/%s/" % (id))
                    crop_img_file_name = ("%s%s.jpg" % (directory, formatted_t))

                    # write cropped image to training folder
                    #cv2.imwrite(crop_img_file_name, crop_img)
                    #saved_img = Image.fromarray(crop_img)
                    #saved_img.save(crop_img_file_name)
                    #print crop_img_file_name

                ###################
                #### Alignment ####
                ###################
                # aligning face
                landmarks = align.findLandmarks(rgbImg, bb)
                alignedFace = align.align(96, rgbImg, bb,
                                    landmarks=landmarks,
                                    landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)

                if alignedFace is None:
                    # break out of this bb for-loop
                    continue

                phash = None

                if self.id is not None: # training mode
                    # unique hash from alignedFace image
                    phash = str(imagehash.phash(Image.fromarray(alignedFace)))

                if phash is not None and phash in self.images:
                    identity = self.images[phash].identity
                    #print 'Found existing phash'
                    #print self.images[phash]
                    
                else:
                    #print 'new phash ' + str(len(self.images)) 
                    rep = net.forward(alignedFace)
                    #print rep

                    #####################
                    #### Recognition ####
                    #####################
                    if self.id is None: 
                        if VideoCamera.trainer is not None:
                            prediction = VideoCamera.trainer.predictFace(rep)

                            user = prediction["user"]
                            confidence = prediction["confidence"] * 100

                            # draw text
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            line_type = cv2.CV_AA

                            if user is not None:
                                cv2.putText(self.frame, "{} {:.1f}%".format(user.username, confidence), (bb.left(), bb.top() - 10), font, 0.6, (0, 255, 0), 1, line_type)
                            else:
                                cv2.putText(self.frame, "Unknown", (bb.left(), bb.top() - 10), font, 0.6, (0, 255, 0), 1, line_type)

                        else:
                            print '[Error] class variable trainer is None.'
                        
                    else:
                        # self.id is not none, means it is training mode
                        # add new face to images array if training mode
                        self.images[phash] = Face(rep, self.id)
                        #print self.images
                    
            # end of openface face detection

    def process_frame(self):
        bb = None
        bbProcess = Process(target=self.get_bounding_box)
        bbProcess.start()
        bbProcess.join()

    def get_frame(self, hasMultiple=None, id=None):
        ret, self.frame = self.cam.read()
        self.frame = cv2.flip(self.frame, 1)
        #frame = self.cam.read()

        # resized for speed 
        # width=320:20fps, 480:11fps, 640:6fps
        #self.frame = imutils.resize(self.frame, width=640)
        self.get_bounding_box(hasMultiple, id)

        ret3, jpeg = cv2.imencode('.jpg', self.frame)
        self.fps.update()

        return jpeg.tostring()

    ##################
    #### Clean Up ####
    ##################
    def __del__(self):
        #self.cam.stop()
        self.cam.release()
        cv2.destroyAllWindows()
        self.fps.stop()
        print "[INFO] approx. FPS: {:.2f}".format(self.fps.fps())
        print "[INFO] total images for this session: {}".format(len(self.images))

        if self.id: # only update db and train svm if training mode is on
            VideoCamera.trainer.trainSVM(self.images)
        else:
            print '[INFO] this is an inference session hence SVM was not trained.'
