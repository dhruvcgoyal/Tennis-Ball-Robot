Tennis ball collecting robot...

Purpose: An autonomous robot that uses computer vision to gather tennis balls

As a competitive tennis player, I decided to try to ease the tedious task of picking up tennis balls that are scattered around the court

Current Status: V1: Tennis ball detecting software is mostly working with motor integration. Fine-tuning needs done

Hardware: Raspberry Pi 4
          Pi Cam 3
          MicroSD
          L298n motor driver
          3.4V-7V DC Motors and wheels kit
          9V Rechargeable Lithium-Ion battery
          5V buck converter
          5V portable power bank
          3D printed car body
          

Roadmap:

V1: Detect and drive towards a singular tennis ball

      How it works: The while loop processes each frame
                    Frame is blurred, changed to HSV colorspace, and finally, a mask is created via the cv2.inRange function, defined by the HSV limits declared at the beginning
                    If anything in the frame matches the colour range, then a minimum enclosing circle function is applied to it to determine its circularity
                    If the contour is circular, then it is added to a list of valid contours (contours that are tennis balls)
                    If the valid contour with the largest area remains the same for 3 consecutive frames, a bounding box is drawn around it for visual aid
                    If the ball is off the center of the camera frame, then the motors turn to bring the robot to face the ball
                    

V2: Choose the closest target out of multiple tennis balls and drive towards it, while being able to avoid obstacles in the way

V3: Be able to collect the ball and return it to a specific point on the court

So far, I have learned the basic concepts of computer vision, such as HSV color space use cases, contour detection, circularity, real-time frame processing, and how to implement them using OpenCV.
I have learned how to use a Raspberry Pi via Linux, SSH remote development, and deploying Python to a Raspberry Pi
I learned how to debug systematically, breaking complex problems into isolated components, testing each independently, and using diagnostic code to identify root causes rather than guessing.

        
