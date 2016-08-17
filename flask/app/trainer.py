import numpy as np

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC
from app import db
from app.models import Face, FaceImage, User
import json

class Trainer(object):

	def __init__(self):
		self.totalImages = {}
		self.svm = None
		self.trainSVM(None)

	##################
	#### Training ####
	##################
	def getData(self):
		X = []
		y = []
		
		for img in self.totalImages.values():
			X.append(img.rep)
			y.append(img.identity)

		numIdentities = len(set(y + [-1])) - 1
		
		if numIdentities == 0:
			return None

		# if args.unknown:
		# 	numUnknown = y.count(-1)
		# 	numIdentified = len(y) - numUnknown
		# 	numUnknownAdd = (numIdentified / numIdentities) - numUnknown
		# 	if numUnknownAdd > 0:
		# 		print("+ Augmenting with {} unknown images.".format(numUnknownAdd))
		# 		for rep in self.unknownImgs[:numUnknownAdd]:
		# 			# print(rep)
		# 			X.append(rep)
		# 			y.append(-1)

		X = np.vstack(X)
		y = np.array(y)

		return (X, y)

	def retrieveFaceImage(self, images=None):
		if images is not None:
			# write to db, combine with the other user images
			for key in images:
				value = images[key]
				
				faceImage = FaceImage(key, value.identity, json.dumps(value.rep.tolist()))
				db.session.add(faceImage)
				db.session.commit()

		# rebuild self.images from db FaceImage data
		faceImages = db.session.query(FaceImage).all()
		self.totalImages = {}

		for faceImage in faceImages:
			# retrieve properties
			phash = str(faceImage.phash)
			identity = faceImage.identity
			# convert rep string to numpy array
			repDecoded = json.loads(faceImage.rep)
			repArray = np.array(repDecoded)

			self.totalImages[phash] = Face(repArray, identity)

		# len(self.totalImage) might be < len(faceImages) due to overlapping phash
		print "[INFO] total face images: {}".format(len(faceImages))
		print "[INFO] total images: {}".format(len(self.totalImages))

		return self.totalImages

	def trainSVM(self, images):
		self.retrieveFaceImage(images)

		if len(self.totalImages) > 0:
			print "+ Training SVM on {} labeled images.".format(len(self.totalImages))

			d = self.getData()
			
			if d is None:
				print 'd is None'
				self.svm = None
				return
			else:
				(X, y) = d

				numIdentities = len(set(y + [-1]))
				#print set(y + [-1]) # adds -1 to every element, i.e. 2 + (-1) = 1

				if numIdentities <= 1:
					print 'numIdentities <= 1'
					return

				param_grid = [{
					'C': [1, 10, 100, 1000],
					'kernel': ['linear']
				}, {
					'C': [1, 10, 100, 1000],
					'gamma': [0.001, 0.0001],
					'kernel': ['rbf']
				}]

				self.svm = GridSearchCV(SVC(C=1), param_grid, cv=5).fit(X, y)
				print "+ SVM trained and fitted successfully."

	def predictFace(self, rep):

		if self.svm is None:
			print self.svm
			self.trainSVM(None)

		#print 'Muahaha prediction!'
		rep = rep.reshape(1, -1)
		identity = self.svm.predict(rep)[0]

		user = db.session.query(User).get(identity)

		#print user.username

		return user