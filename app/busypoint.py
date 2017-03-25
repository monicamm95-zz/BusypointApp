import numpy as np
import cv2
from crying import totalFaces as faces
from array import array

waittime = 0

def frameOneCheck(x, prev_x):
	if prev_x == 0 or x > prev_x:
		return True
	return False

def isSameFirstPerson(x, prev_x, colour, prev_colour, maxPixelDist, CPD): 	
	if x > prev_x or abs(x - prev_x) < maxPixelDist:
		if checkColourDiff(colour, prev_colour, CPD): 
			return True
	return False

# Checks the RGB values of the face and compares it to the previous face
def checkColourDiff(colour, prev_colour, CPD):
	if abs(colour[0] - prev_colour[0])/255*100 < CPD and abs(colour[1] - prev_colour[1])/255*100 < CPD and abs(colour[2] - prev_colour[2])/255*100 < CPD:
		return True
	return False

def myround(x, base=25):
    return int(base * round(float(x)/base))

def median(lst):
    return np.median(np.array(lst))

#  This code counts how many frames somebody has been at the front of the line for.
# When they leave the line, the frame count is added to the "waitList"
# The average of the "waitList" multiplied by the number of people in line gives an approximate wait time.

def getWaitTime(videoName):

	#Capture Video
	cap1 = cv2.VideoCapture('test0.mp4')

	#Background Subtraction
	fgbg = cv2.BackgroundSubtractorMOG()

	#Initialize global vars
	count = 0
	minPixelList = list()
	maxPixelList = list()
	numPeopleList = list()
	prevDist = 0;
	avgFirstWaitime = -1;
	avgnumPeople = 0;

	face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	profileface_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

	miaFrames = 160
	# Max distance to be considered the same face
	maxPixelDist = 80
	# Colour percent difference allowed 
	CPD = 10
	cap = cv2.VideoCapture(videoName)
	fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
	width = cap.get(3)
	height = cap.get(4)

	prev_x = 0
	prev_colour = [0, 0, 0]
	frameCount = 0
	faceFound = False
	i = 0
	frameBuffer = 0
	waitList = []
	while True:
		count = count+1;

		ret, frame = cap1.read()
		global waittime
		 
		fgmask = fgbg.apply(frame)
		img_bw = 255*fgmask.astype('uint8')

		#Morphological operation - closing (dillation => erosion)
		se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
		se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
		mask = cv2.morphologyEx(img_bw, cv2.MORPH_CLOSE, se1)
		mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se2)
		out = fgmask * mask
		 
		#Blob detection parameters
		params = cv2.SimpleBlobDetector_Params()
		params.minThreshold = 10
		params.maxThreshold = 200
		#params.thresholdStep = 50;
		params.blobColor = 255
		params.filterByColor = False
		params.minArea = 30
		params.filterByArea = True

		#Blob detection
		detector = cv2.SimpleBlobDetector(params)
		keypoints = detector.detect(out)
		x = len(keypoints)
		maxPixel = 0;
		minPixel = 10000;

		#Find min and max corrinates (left and right most pixels)
		for keyPoint in keypoints:
			xCoord = keyPoint.pt[0]
			yCoord = keyPoint.pt[1]
			size = keyPoint.size
			maxPixel = int(max(maxPixel, xCoord))
			minPixel = int(min(minPixel, xCoord))

			#minPixel = myround(minPixel);

		#Don't add default min/max pixel values
		if (minPixel != 10000):
			minPixelList.append(minPixel)

		if (maxPixel != 0):
			maxPixelList.append(maxPixel)

		#Draws green circles on detected blobs
		#im_with_keypoints = cv2.drawKeypoints(out, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

		# Show blobs
		#cv2.imshow("Keypoints", im_with_keypoints)

		#if (count%5 == 0 and minPixel != 10000):
		#print(minPixel)

		#Sorts and prunes noise from data set
		if (count % 45 == 0 and len(minPixelList) != 0):
			minPixelList.sort()
			maxPixelList.sort()
			minPixelList = minPixelList[:len(minPixelList)/2]
			medMin = int(median(minPixelList))
			maxPixelList = maxPixelList[len(maxPixelList)/2:]
			medMax = int(median(maxPixelList))
			dist = medMax - medMin
			numPeople = dist/83
			diff = abs(dist - prevDist)
			numPeopleList.append(numPeople)
			del minPixelList[:] 
			del maxPixelList[:] 
			prevDist = dist

		  #Every 6s, produce an estimated number of people for the last 6 seconds on average
		if (count % 180 == 0):
			medNumPeople = int(median(numPeopleList))
			numPeopleList.sort()
			numPeopleList.append(medNumPeople)
			avgnumPeople = int(median(numPeopleList));
			#print(medNumPeople);
			del numPeopleList[:] 
			avgWaitTime = (avgFirstWaitime * medNumPeople) / (30);
			time = count / 30;
			#if (avgWaitTime >= 0):
				#print count, avgWaitTime;


		i += 1
		faceFound = False
		ret, frame = cap.read()
		cv2.putText(frame,str(fps),(10,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1)
		# Iterates through each face found this frame
		if i > len(faces) - 1:
			return np.average(waitList)
		for face in faces[i]:
			(x,y,w,h) = face
			cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
			roi_color = frame[y:y+h, x:x+w]
			colour = np.average(np.average(roi_color, axis=0), axis=0)
			# This check is done on frames where there is no "first" face
			if i == 1 or prev_x == 0:
				if frameOneCheck(x, prev_x):
					prev_x = x
					prev_colour = colour
			# checks if this face is same as the previous first person in line
			elif isSameFirstPerson(x, prev_x, colour, prev_colour, maxPixelDist, CPD):
				faceFound = True
				prev_x = x
				prev_colour = colour
		
		if faceFound:
			frameCount += 1 + frameBuffer
			frameBuffer = 0
		# if face was not found this frame but has been in the previous 90 frames
		elif frameBuffer < 90:
			frameBuffer += 1
		# Face no longer found, assume person has left the line
		else:
			# only add the value to the average if it is within 20% of the average (to remove outliers)
			if len(waitList) == 0 or frameCount > 0.2*np.average(waitList):
				waitList.append(frameCount)
				avgFirstWaitime = np.average(waitList);
			#  reset all the values
			frameBuffer = 0
			frameCount = 0
			prev_x = 0
			prev_colour = [0, 0, 0]
		cv2.putText(frame, str(frameCount),(500,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),1)
		k = cv2.waitKey(50) & 0xff
		cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
		cv2.imshow('frame', frame)
		cv2.resizeWindow('frame', int(width),int(height))
		waittime = int(avgnumPeople * avgFirstWaitime)

		if(i % 90 == 0 and waittime >= 0):
			print i, avgFirstWaitime, avgnumPeople, waittime;
			file = open("temp.txt", "w")
			file.write(str(waittime))
			file.close()
		#file = open("temp.txt", "w")
    	#file.write(num)
    	#file.close()

		if k == 27:
			break
	cap.release()
	cv2.destroyAllWindows()

getWaitTime("crying.m4v")