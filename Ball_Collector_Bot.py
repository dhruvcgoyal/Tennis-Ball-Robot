import cv2 
import numpy as np
from flask import Flask, Response
app = Flask(__name__)
from picamera2 import Picamera2


lower = np.array([25, 75, 85])
upper = np.array([50, 220, 255])

picam = Picamera2()
picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
picam.start()

history = []
history_size = 3
pos_thresh = 30

def generate_frames():
    while True:
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        
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
                    xs = [pos[0] for pos in history]
                    ys = [pos[1] for pos in history]

                    if (max(xs) - min(xs)) < pos_thresh and (max(ys) - min(ys)) < pos_thresh:
                        stable = True
            else:
                history.clear()

            if stable:
                cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
                


        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        
@app.route('/video')
def video_feed():
    # mimetype tells browser this is a continuous stream of JPEGs
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    # Tiny HTML page with image tag pointing to /video
    return '<img src="/video" width="800">'

# Start the web server — visible to all devices on WiFi on port 5000
app.run(host='0.0.0.0', port=5000, debug=False)


