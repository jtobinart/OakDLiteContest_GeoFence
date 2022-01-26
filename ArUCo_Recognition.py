# ArUCo Maker Recognition
# Author: James Tobin
# Notes:
'''
  Portions of this code was sourced from depthai_colorcam_demo.py and modified
  example code form, I believe, pyimagesearch
'''

import cv2
import numpy as np
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutRgb = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")

# Properties
camRgb.setPreviewSize(300, 300)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

# Linking
camRgb.preview.link(xoutRgb.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    print('Connected cameras: ', device.getConnectedCameras())
    # Print out usb speed
    print('Usb speed: ', device.getUsbSpeed().name)

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    aruco_dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
    aruco_parameters = cv2.aruco.DetectorParameters_create()

    while True:
        inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
        frame = inRgb.getCvFrame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers in the video frame
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, aruco_dictionary, parameters=aruco_parameters)
        
        # Check that at least one ArUco marker was detected
        if len(corners) > 0:
          # Flatten the ArUco IDs list
          ids = ids.flatten()
          
          # Loop over the detected ArUco corners
          for (marker_corner, marker_id) in zip(corners, ids):
              if marker_id
          
            # Extract the marker corners
            corners = marker_corner.reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners
            
            # Convert the (x,y) coordinate pairs to integers
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
            top_left = (int(top_left[0]), int(top_left[1]))
            
            # Draw the bounding box of the ArUco detection
            cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
            cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
            cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
            cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)
            
            # Calculate and draw the center of the ArUco marker
            center_x = int((top_left[0] + bottom_right[0]) / 2.0)
            center_y = int((top_left[1] + bottom_right[1]) / 2.0)
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)
            
            # Draw the ArUco marker ID on the video frame
            # The ID is always located at the top_left of the ArUco marker
            cv2.putText(frame, str(marker_id), 
              (top_left[0], top_left[1] - 15),
              cv2.FONT_HERSHEY_SIMPLEX,
              0.5, (0, 255, 0), 2)
      
        # Retrieve 'bgr' (opencv format) frame
        cv2.imshow("rgb", frame)

        if cv2.waitKey(1) == ord('q'):
            break