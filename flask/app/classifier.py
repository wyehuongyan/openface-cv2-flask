import argparse
import openface

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '../..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

class Classifier(object):

	def __init__(self):
		parser = argparse.ArgumentParser()

		parser.add_argument('--dlibFacePredictor', type=str,
							help="Path to dlib's face predictor.",
							default=os.path.join(dlibModelDir,
												"shape_predictor_68_face_landmarks.dat"))
		parser.add_argument('--networkModel', type=str,
							help="Path to Torch network model.",
							default=os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'))
		parser.add_argument('--imgDim', type=int,
							help="Default image dimension.", default=96)
		parser.add_argument('--cuda', action='store_true')
		parser.add_argument('--verbose', action='store_true')

		subparsers = parser.add_subparsers(dest='mode', help="Mode")
		trainParser = subparsers.add_parser('train',
											help="Train a new classifier.")
		trainParser.add_argument('--ldaDim', type=int, default=-1)
		trainParser.add_argument('--classifier', type=str,
								choices=['LinearSvm', 'GMM'],
								help='The type of classifier to use.',
								default='LinearSvm')
		trainParser.add_argument('workDir', type=str,
								help="The input work directory containing 'reps.csv' and 'labels.csv'. Obtained from aligning a directory with 'align-dlib' and getting the representations with 'batch-represent'.")

		inferParser = subparsers.add_parser('infer',
											help='Predict who an image contains from a trained classifier.')
		inferParser.add_argument('classifierModel', type=str,
								help='The Python pickle representing the classifier. This is NOT the Torch network model, which can be set with --networkModel.')
		inferParser.add_argument('imgs', type=str, nargs='+',
								help="Input image.")

		args = parser.parse_args()
		if args.verbose:
			print("Argument parsing and import libraries took {} seconds.".format(
				time.time() - start))

		if args.mode == 'infer' and args.classifierModel.endswith(".t7"):
			raise Exception("""
	Torch network model passed as the classification model,
	which should be a Python pickle (.pkl)

	See the documentation for the distinction between the Torch
	network and classification models:

			http://cmusatyalab.github.io/openface/demo-3-classifier/
			http://cmusatyalab.github.io/openface/training-new-models/

	Use `--networkModel` to set a non-standard Torch network model.""")
		start = time.time()

		align = openface.AlignDlib(args.dlibFacePredictor)
		net = openface.TorchNeuralNet(args.networkModel, imgDim=args.imgDim,
									cuda=args.cuda)

		if args.verbose:
			print("Loading the dlib and OpenFace models took {} seconds.".format(
				time.time() - start))
			start = time.time()
	
	def boundingBox(frame):
		rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		bb = align.getLargestFaceBoundingBox(rgbImg)
		if bb is None:
			raise Exception("Unable to find a face: {}".format(imgPath))
		if args.verbose:
			print("Face detection took {} seconds.".format(time.time() - start))

		start = time.time()
		alignedFace = align.align_v1(args.imgDim, rgbImg, bb,
									landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
		if alignedFace is None:
			raise Exception("Unable to align image: {}".format(imgPath))
		if args.verbose:
			print("Alignment took {} seconds.".format(time.time() - start))

		return bb