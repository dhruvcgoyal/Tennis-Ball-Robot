import cv2 
import numpy as np
from flask import Flask, Response
app = Flask(__name__)
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time

IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 23
ENA = 18
ENB = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

pwm_a = GPIO.PWM(ENA, 100)
pwm_b = GPIO.PWM(ENB, 100)
pwm_a.start(0)
pwm_b.start(0)

lower = np.array([25, 50, 50])
upper = np.array([50, 220, 255])

picam = Picamera2()
picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
picam.start()

history = []
history_size = 3
pos_thresh = 30


def adjust(cx):

    limit_low = 100
    limit_high = 540

    if cx < limit_low:
        left(50)
        print("L")

    elif cx > limit_high:
        right(50)
        print("R")

    else:
        forward(100)
        print("tung")
        





def backward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)



def stop():
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)



def left(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)


def right(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)



def forward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)



def generate_frames():
    while True:
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        

        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blur = cv2.GaussianBlur(hsv, (11, 11), 0)
        mask = cv2.inRange(blur, lower, upper)
        kernel = np.ones((15,15), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        
        
        
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
                cx = x + w//2
                cy = y + h//2

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
                stop()

            if stable:
                cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
                cv2.line(frame, (320, 0), (320, 480), (255, 0, 0), 2)
                cv2.putText(frame, f"cx={cx}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
                
                adjust(cx)
                


        ret, buffer = cv2.imencode('.jpg', mask, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
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




