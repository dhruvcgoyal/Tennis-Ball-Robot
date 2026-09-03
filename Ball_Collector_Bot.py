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
picam.configure(picam.create_video_configuration(main={"size": (320, 240)}))
picam.start()

history = []
history_size = 3
pos_thresh = 30

frame_count = 0
stable = False

best_area = 0
best_box = None
cx = None

direction = None


def adjust(cx):
    global direction

    limit_low = 100
    limit_high = 220

    if cx < limit_low:

        if direction != "left":
            direction = "left"
            stop()
            time.sleep(1)

        else:
            left(70)
            print("L")

    elif cx > limit_high:

        if direction != "right":
            direction = "right"
            stop()
            time.sleep(1)

        else:
            right(70)
            print("R")

    elif 10000 >= best_area >= 5000:

        if direction != "slow_forward":
            direction = "slow_forward"
            stop()
            time.sleep(1)

        else:
            forward(60)
            print("Tripi")

    else:

        if direction != "fast_forward":
            direction = "fast_forward"
            stop()
            time.sleep(1)

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
    global frame_count, stable, best_box, best_area, cx
    while True:
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_count += 1
        

        if frame_count % 2 == 0:
            best_area = 0
            results = model(frame, verbose=False)
            #print(f"detections: {len(results[0].boxes)}")

            
            detected = False
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if len(boxes) > 0:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        
                        if confidence > 0.5:
                            detected = True
                            area = (x2-x1) * (y2-y1)
                            if area > best_area:
                                best_area = area
                                best_box = (x1, y1, x2, y2)
                            
                if detected:
                    x1, y1, x2, y2 = best_box
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2            
                    history.append((cx, cy))
                    stable = True
                    #if len(history) > history_size:
                        #history.pop(0)
                            
                #if len(history) == history_size:
                    #xs = [pos[0] for pos in history]
                    #ys = [pos[1] for pos in history]
                    #if (max(xs) - min(xs)) < pos_thresh and (max(ys) - min(ys)) < pos_thresh:
                        #stable = True

            if not detected:
                history.clear()
                stable = False
                stop()

        if stable:
            
             

                
            if best_area >= 10000 and 100 < cx < 220:
                cv2.rectangle(frame, best_box[:2], best_box[2:], (0, 255, 0), 2)
                stop()
                print("stopped")

            elif best_area >= 30000:
                cv2.rectangle(frame, best_box[:2], best_box[2:], (0, 255, 0), 2)
                stop()
                print("stopped")

            else:    
                cv2.rectangle(frame, best_box[:2], best_box[2:], (0, 255, 0), 2)
                adjust(cx)
                print(best_area)





            
            

                        

                        
                



                    


            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        
        
        
@app.route('/video')
def video_feed():
     #mimetype tells browser this is a continuous stream of JPEGs
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    # Tiny HTML page with image tag pointing to /video
    return '<img src="/video" width="800">'

 #Start the web server — visible to all devices on WiFi on port 5000
app.run(host='0.0.0.0', port=5000, debug=False)




