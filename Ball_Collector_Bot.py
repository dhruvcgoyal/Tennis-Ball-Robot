import cv2 
import numpy as np
from flask import Flask, Response
app = Flask(__name__)
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time
from ultralytics import YOLO

model = YOLO('best_ncnn_model')

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



picam = Picamera2()
picam.configure(picam.create_video_configuration(main={"size": (640, 480)}))
picam.start()

history = []
history_size = 3
pos_thresh = 30

frame_count = 0
last_box = None
last_cx = None
stable = False


def adjust(cx):

    limit_low = 100
    limit_high = 540

    if cx < limit_low:
        left(80)
        print("L")

    elif cx > limit_high:
        right(80)
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
    global frame_count, last_box, last_cx, stable
    while True:
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_count += 1
        

        if frame_count % 3 == 0:
            results = model(frame, verbose=False)
            print(f"detections: {len(results[0].boxes)}")

            
            detected = False
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if len(boxes) > 0:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        
                        if confidence > 0.5:
                            detected = True
                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2
                            last_box = (x1, y1, x2, y2)
                            last_cx = cx
                            
                            history.append((cx, cy))
                            if len(history) > history_size:
                                history.pop(0)
                            
                            if len(history) == history_size:
                                xs = [pos[0] for pos in history]
                                ys = [pos[1] for pos in history]
                                if (max(xs) - min(xs)) < pos_thresh and (max(ys) - min(ys)) < pos_thresh:
                                    stable = True

            if not detected:
                history.clear()
                last_box = None
                last_cx = None
                stable = False
                stop()

        if stable and last_box and last_cx:
            cv2.rectangle(frame, last_box[:2], last_box[2:], (0, 255, 0), 2)
            adjust(last_cx)





        
        

                    

                    
            



                


        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        
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




