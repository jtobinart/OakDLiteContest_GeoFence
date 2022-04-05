# Python3.8 - rgb_ssdl_api_localization.py
# Version: 1.0
# Author(s): James Tobin
# Acknowledgement: The Depthai pipeline uses demo code provided in the Depthai documentation.

#   MIT License
'''
Copyright (c) 2022 James Tobin
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:
The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
'''
print("=================================================================================================")


#==============================================================================
#==                              VERSION NOTES                               ==
#==============================================================================
'''
v1.0
- Use Luxonis' OAK-D Lite camera to detect when animals leave a perscribed area. The area is established
    using ArUco markers.

IMPLEMENTATION NOTES:
- Animals are often misidentified as other animals. Use range of cat (17) to girraffe (25) and ignore 
    birds (16)

TO DO:
- Polar Coordinates
- ID Tracking
- Fully Integrate IMU
'''


#========================================================================
#==                              IMPORTS                               ==
#========================================================================
from pathlib import Path
import time
import cv2
import depthai
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

Raspberry_Pi = False
if Raspberry_Pi:
    import board
    import adafruit_icm20x

    i2c = board.I2C()  # uses board.SCL and board.SDA
    icm = adafruit_icm20x.ICM20948(i2c)

    imu_xyz = []
    for i in range(5):
        x, y, z = icm.magnetic
        imu_xyz.append([x,y,z])
    print(imu_xyz)


#==========================================================================
#==                              VARIABLES                               ==
#==========================================================================

# Movement Function Variables
frame0 = np.zeros((300,300,3))
framenth = np.zeros((300,300,3))
frameCount = 0

# Setting State Variable
scan = True
move = True

# Marker Location Array
foundMarkers = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

imu_cal = [[67.8, 3.5190],[35.1, 3.2345],[57.6, 2.7523]]

# ArUCo dictionary and parameters
aruco_Dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
aruco_Parameters = cv2.aruco.DetectorParameters_create()

labelmap = [ "background", "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", 
                "truck", "boat", "traffic light", "fire hydrant", "N/A", "stop sign",  "parking meter",
                "bench",  "bird", "cat", "dog", "horse", "sheep", "cow",  "elephant",
                "bear",  "zebra",  "giraffe", "N/A", "backpack", "umbrella",  "N/A",  "N/A", "handbag", 
                "tie", "suitcase",  "frisbee",  "skis",  "snowboard", "sports ball", "kite", 
                "baseball bat", "baseball glove", "skateboard",  "surfboard",  "tennis racket", 
                "bottle", "N/A", "wine glass", "cup", "fork", "knife", "spoon", "bowl", 
                "banana",  "apple",  "sandwich",  "orange",  "broccoli", "carrot", "hot dog", 
                "pizza", "donut", "cake",  "chair",  "couch",  "potted plant",  "bed",  "N/A",
                "dining table", "N/A", "N/A", "toilet", "N/A",  "tv",  "laptop",  "mouse",  "remote",  
                "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",  "refrigerator", "N/A", 
                "book", "clock",  "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]


#==========================================================================
#==                              FUNCTIONS                               ==
#==========================================================================

#=================================== Motion Tracking Matching ===================================
def MotionTrackingMatching(current_frame, nth_frame, count):
    global horizontal_line, vertical_line

    if count > 19 and count % 5 == 0:
        current_frame = cv2.cvtColor(current_frame,cv2.COLOR_BGR2GRAY)
        nth_frame = cv2.cvtColor(nth_frame,cv2.COLOR_BGR2GRAY)
        
        # Define ROI coordinates
        x1 = int(current_frame.shape[1]*0.3)
        x2 = int(current_frame.shape[1]*0.7)
        y1 = int(current_frame.shape[0]*0.3)
        y2 = int(current_frame.shape[0]*0.7)
        frameROI = current_frame[y1:y2, x1:x2]

        # Match ROI from nth_frame to current_frame
        result = cv2.matchTemplate(nth_frame, frameROI, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)

        # Calculate Difference between ROI regions between current_frame and nth_frame 
        delta_x = (current_frame.shape[1]/2) - (max_loc[0] + (frameROI.shape[1]/2))
        delta_y = (current_frame.shape[0]/2) - (max_loc[1] + (frameROI.shape[0]/2))
        return int(delta_x), int(delta_y)
    return 0,0

#=================================== IMU Update ===================================
def IMU_Update():
    global imu_cal, imu_xyz
    zTotal = 0
    xTotal = 0

    x, y, z = icm.magnetic

    x = int((x + imu_cal[2][0])*imu_cal[2][1])
    y = int((y + imu_cal[2][0])*imu_cal[2][1])
    z = int((z + imu_cal[2][0])*imu_cal[2][1])
    imu_xyz.append([x,y,z])

    #Use for dx
    for i in range(len(imu_xyz)):
        zTotal += imu_xyz[i][2]
    
    #Use for dy
    for i in range(len(imu_xyz)):
        xTotal += imu_xyz[i][1]
        
    dx = int((zTotal/len(imu_xyz)) - imu_xyz[int(4)][2])
    dy = int((xTotal/len(imu_xyz)) - imu_xyz[int(4)][1])    
    
    imu_xyz.pop(0)

    return dx , dy
    
#=================================== Find ArUco ===================================
def FindArUco(current_frame):
    global foundMarkers

    # Detect ArUco markers in the input frame
    (corners, ids, _) = cv2.aruco.detectMarkers(current_frame, aruco_Dictionary, parameters=aruco_Parameters)
    
    # Check if any codes have been detected
    if len(corners) > 0:
        # Flatten the markers' IDs list
        ids = ids.flatten()
        
        # Loop through the detected markers' corners
        for (marker_Corner, marker_ID) in zip(corners, ids):
            corners = marker_Corner.reshape((4, 2))
            (topLeft, _, bottomRight, _) = corners
            
            # Convert variables to integers in an (x, y) format
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            
            # Calculate the center of the markers
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)

            # Set/Update found markers' locations
            if marker_ID == 5:
                foundMarkers[0][0] = cX
                foundMarkers[0][1] = cY
                foundMarkers[0][2] = 1
                continue
            elif marker_ID == 277:
                foundMarkers[1][0] = cX
                foundMarkers[1][1] = cY
                foundMarkers[1][2] = 1 
                continue
            elif marker_ID == 965:
                foundMarkers[2][0] = cX
                foundMarkers[2][1] = cY
                foundMarkers[2][2] = 1
                continue
            elif marker_ID == 981:
                foundMarkers[3][0] = cX
                foundMarkers[3][1] = cY
                foundMarkers[3][2] = 1
                continue

#=================================== Frame Normalization ===================================
def frameNorm(frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


#===============================================================================
#==                              SETUP PIPELINE                               ==
#===============================================================================

pipeline = depthai.Pipeline()

cam_rgb = pipeline.createColorCamera()
cam_rgb.setImageOrientation(depthai.CameraImageOrientation.ROTATE_180_DEG)  #Flip color camera
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setInterleaved(False)

detection_nn = pipeline.createMobileNetDetectionNetwork()
detection_nn.setBlobPath(str((Path(__file__).parent / Path('ssdlite_mobilenet_v2.blob')).resolve().absolute()))
detection_nn.setConfidenceThreshold(0.5)
cam_rgb.preview.link(detection_nn.input)

xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

xout_nn = pipeline.createXLinkOut()
xout_nn.setStreamName("nn")
detection_nn.out.link(xout_nn.input)


#==========================================================================
#==                              MAIN LOOP                               ==
#==========================================================================

with depthai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue("rgb")
    q_nn = device.getOutputQueue("nn")

    frame = None
    detections = []

    while True:
        in_rgb = q_rgb.tryGet()
        in_nn = q_nn.tryGet()

        if in_rgb is not None:
            frame = in_rgb.getCvFrame()

        if in_nn is not None:
            detections = in_nn.detections

        if frame is not None:
            #Scan for ArUco Markers
            if scan == True:
                FindArUco(frame)
            
            #Predict markers' location
            if move == True:
                if Raspberry_Pi:
                    dx, dy = IMU_Update()
                else:
                    dx, dy = MotionTrackingMatching(frame.copy(), framenth.copy(), frameCount)
            else:
                dx = 0
                dy = 0
            
            #Update markers' locations based on prediction
            for i in range(len(foundMarkers)):
                if foundMarkers[i][2] == 1:
                    foundMarkers[i][0] += dx
                    foundMarkers[i][1] += dy
                cv2.circle(frame, (foundMarkers[i][0], foundMarkers[i][1]), 4, (0, 0, 255), -1)
            
            # Draw Lines of Polygon
            for i in range(len(foundMarkers)):
                next = (i+1)%len(foundMarkers)
                if foundMarkers[i][2] == 1 and foundMarkers[next][2] == 1:
                    cv2.line(frame, (foundMarkers[i][0],foundMarkers[i][1]),(foundMarkers[next][0],foundMarkers[next][1]), (255,0,0),2)

            # Save frames to compare to later
            if frameCount % 5 == 0:
                framenth = frame.copy()
            frame0 = frame.copy()
            frameCount += 1
            
            #Setup 
            polygon = Polygon([(foundMarkers[0][0], foundMarkers[0][1]), (foundMarkers[0][0], foundMarkers[0][1]), (foundMarkers[1][0], foundMarkers[1][1]), (foundMarkers[2][0], foundMarkers[2][1]), (foundMarkers[3][0], foundMarkers[3][1])])

            #Show NN Detections
            for detection in detections:
                if detection.label > 15 and detection.label < 27:
                    bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                    
                    #Find center of detection box
                    cx = bbox[0] + int((bbox[2] - bbox[0])/2)
                    cy = bbox[1] + int((bbox[3] - bbox[1])/2)
                    
                    #Create point
                    point = Point(cx, cy)
                    
                    #Check if point is inside polygon
                    if polygon.contains(point):
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    #Draw detection box and point and print detection ID   
                    cv2.circle(frame, (cx, cy), 2, color, -1)
                    cv2.putText(frame, str(detection.label), (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

            cv2.imshow("preview", frame)

        #Keyboard hotkeys
        key = cv2.waitKey(1) & 0xFF
    
        if key == ord("q"):
            break
        elif key == ord("t"):
            scan = not scan
            print(scan)
        elif key == ord("m"):
            move = not move
            print(move)
        elif key == ord("S"):
            print("Saving Photo")
            if Raspberry_Pi:
                new_filename = str(time.time_ns())+'.jpg'
            else:
                new_filename = 'photos/screenshots/'+str(time.time_ns())+'.jpg'
            cv2.imwrite(str((Path(__file__).parent / Path(new_filename)).resolve().absolute()), frame)