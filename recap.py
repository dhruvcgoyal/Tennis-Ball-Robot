import cv2 
import numpy as np


lower = np.array([25, 75, 85])
upper = np.array([50, 220, 255])

cam = cv2.VideoCapture(0)

history = []
history_size = 3
pos_thresh = 30

while True:
    ret, frame = cam.read()

    if ret == False:
        break

    frame = cv2.resize(frame, (1280, 720))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blur = cv2.GaussianBlur(hsv, (11, 11), 0)
    mask = cv2.inRange(blur, lower, upper)

    
    
    
    contours, heirarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours)>0:

        

        valid = []

        for suspect in contours:
        
            (x, y), radius = cv2.minEnclosingCircle(suspect)
            circle_area = 3.14159 * radius * radius
            area = cv2.contourArea(suspect)

            circularity = area / circle_area

            

            if circularity > 0.5 and area > 500:
                
                valid.append(suspect)
                

                
        stable = False

        if len(valid) > 0:

            
            target = max(valid, key = cv2.contourArea)

                   
            x, y, w, h = cv2.boundingRect(target)
            cx = (x + w)//2
            cy = (y + h)//2

            history.append((cx, cy))

            if len(history) > history_size:
                history.pop(0)

            

            if len(history) == history_size:
                xs = [h[0] for h in history]
                ys = [h[1] for h in history]

                if (max(xs) - min(xs)) < pos_thresh and (max(ys) - min(ys)) < pos_thresh:
                    stable = True
        else:
            history.clear()

        if stable:
            cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)


    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)
    
    
    if cv2.waitKey(40) & 0xFF == ord("q"):
        break



cam.release()
cv2.destroyAllWindows()