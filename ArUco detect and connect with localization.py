# import the necessary packages
import time
import cv2
import numpy as np
import sys

print("=================================================================================================================================")

frame0 = np.zeros((300,300,3))
framenth = np.zeros((300,300,3))
frameCount = 0

lastCoordinates = (320, 179)
setupflag = True
scan = True

foundMarkers = [[0,0,0],[0,0,0],[0,0,0]]

# load the ArUCo dictionary and grab the ArUCo parameters
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
arucoParams = cv2.aruco.DetectorParameters_create()

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
cap = cv2.VideoCapture(0)
time.sleep(2.0)

def MotionTrackingMatching(frame, frameLast, frameTen, count):
    global lastCoordinates, horizontal_line, vertical_line
    img = frame.copy()
    #text = "error"
    noiseTolerance = 10
    if count > 19 and count % 5 == 0:
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        frameTen = cv2.cvtColor(frameTen,cv2.COLOR_BGR2GRAY)
        
        #Define ROI coordinates
        #x1 = int(frame.shape[1]/4)
        #x2 = x1*3
        #y1 = int(frame.shape[0]/4)
        #y2 = y1*3
        x1 = int(frame.shape[1]*0.3)
        x2 = int(frame.shape[1]*0.7)
        y1 = int(frame.shape[0]*0.3)
        y2 = int(frame.shape[0]*0.7)
        frameROI = frame[y1:y2, x1:x2]

        #Match them
        result = cv2.matchTemplate(frameTen, frameROI, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        #Locate on color image - result is the size of frameROI
        #location = (max_loc[0]*2,max_loc[1]*2)
        #locationStart = ((max_loc[0]*2)-(frameROI.shape[1]/2),(max_loc[1]*2)-(frameROI.shape[0]/2))
        #locationEnd = ((max_loc[0]*2)+(frameROI.shape[1]/2),(max_loc[1]*2)+(frameROI.shape[0]/2))
        location = int((max_loc[0])+(frameROI.shape[1]/2)),int((max_loc[1])+(frameROI.shape[0]/2))
        #locationStart = (max_loc[0],max_loc[1])
        #locationEnd = ((max_loc[0])+(frameROI.shape[1]),(max_loc[1])+(frameROI.shape[0]))
        #print(location)
        #Draw results
        xMovement = lastCoordinates[0] - location[0]
        yMovement = lastCoordinates[1] - location[1]
        return xMovement, yMovement

        '''
        if xMovement >= -noiseTolerance and xMovement <= noiseTolerance and yMovement >= -noiseTolerance and yMovement <= noiseTolerance:
            text = "stopped" # center
        elif xMovement < -noiseTolerance and yMovement >= -noiseTolerance and yMovement <= noiseTolerance:
            text = "right" #right
        elif xMovement > noiseTolerance and yMovement >= -noiseTolerance and yMovement <= noiseTolerance:
            text = "left" #left
        elif xMovement >= -noiseTolerance and xMovement <= noiseTolerance and yMovement < -noiseTolerance:
            text = "forwards" #up
        elif xMovement >= -noiseTolerance and xMovement <= noiseTolerance and yMovement > noiseTolerance:
            text = "backwards" #down
        elif xMovement < -noiseTolerance and yMovement < -noiseTolerance:
            text = "forwards and right" #upper right
        elif xMovement > noiseTolerance and yMovement < -noiseTolerance:
            text = "forwards and left" #upper left
        elif xMovement < -noiseTolerance and yMovement > noiseTolerance:
            text = "backwards and right" #lower right
        elif xMovement > noiseTolerance and yMovement > noiseTolerance:
            text = "backwards and left" #lower left
        
        #cv2.circle(img, location, 15,255,2)

        horizontal_line[0] += xMovement
        horizontal_line[1] += yMovement
        horizontal_line[2] += xMovement
        horizontal_line[3] += yMovement

        vertical_line[0] += xMovement
        vertical_line[1] += yMovement
        vertical_line[2] += xMovement
        vertical_line[3] += yMovement

        cv2.line(img, (horizontal_line[0],horizontal_line[1]), (horizontal_line[2],horizontal_line[3]), (255,0,255), 3)
        cv2.line(img, (vertical_line[0],vertical_line[1]), (vertical_line[2],vertical_line[3]), (255,0,255), 3)
        cv2.rectangle(img, locationStart, locationEnd, (255,0,0), 2)
        cv2.putText(img, text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)   # cv2.putText(frame, text, location, font scale, font color, line type) 
        '''
    return 0,0

def FindArUco(cur_frame):
    global foundMarkers
    frame = cur_frame.copy()
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            
            # convert each of the (x, y)-coordinate pairs to integers
            #topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            #bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            #cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            #cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            #cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            #cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
            
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
           # cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            
            # draw the ArUco marker ID on the frame
            #cv2.putText(frame, str(markerID),(topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if markerID == 965:
                foundMarkers[0][0] = cX
                foundMarkers[0][1] = cY
                foundMarkers[0][2] = 1
                continue
            elif markerID == 981:
                foundMarkers[1][0] = cX
                foundMarkers[1][1] = cY
                foundMarkers[1][2] = 1 
                continue
            elif markerID == 277:
                foundMarkers[2][0] = cX
                foundMarkers[2][1] = cY
                foundMarkers[2][2] = 1
                continue


# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    ret, frame = cap.read()

    frame8 = frame.copy()

    if not ret:
        print("No frame!")
    else:
        frame = cv2.resize(frame, (0,0), fx=0.5,fy=0.5)
        if scan == True:
            FindArUco(frame)
        dx, dy = MotionTrackingMatching(frame.copy(), frame0.copy(), framenth.copy(), frameCount)
        
        
        for i in range(len(foundMarkers)):
            if foundMarkers[i][2] == 1:
                foundMarkers[i][0] += dx
                foundMarkers[i][1] += dy
            cv2.circle(frame, (foundMarkers[i][0], foundMarkers[i][1]), 4, (0, 0, 255), -1)
        
        for i in range(len(foundMarkers)):
            next = (i+1)%len(foundMarkers)
            if foundMarkers[i][2] == 1 and foundMarkers[next][2] == 1:
                cv2.line(frame, (foundMarkers[i][0],foundMarkers[i][1]),(foundMarkers[next][0],foundMarkers[next][1]), (255,0,0),2)

        if frameCount % 5 == 0:
            framenth = frame.copy()
            print(foundMarkers)
        frame0 = frame.copy()
        frameCount += 1
        
        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    elif key == ord("t"):
        scan = not scan
        time.sleep(1)
        print(scan)

# do a bit of cleanup
cv2.destroyAllWindows()