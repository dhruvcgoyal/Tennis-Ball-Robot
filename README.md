Tennis ball collecting robot...

Purpose: An autonomous robot that uses computer vision to gather tennis balls

As a competitive tennis player, I decided to try to ease the tedious task of picking up tennis balls that are scattered around the court

Current Status: V1: Complete

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

      How it works: The while loop processes each frame. Every three frames, the YOLO detection model searches for tennis balls.
      The position of the detection is stored in a list, and if the list has 3 items and the x and y values from each item are extracted, and the max and min are compared.
      If the x and y values are close enough and the confidence is greater than 50%, the ball is driven towards
                    

V2: Choose the closest target out of multiple tennis balls and drive towards it, while being able to avoid obstacles in the way

V3: Be able to collect the ball and return it to a specific point on the court

So far, I have learned the basic concepts of computer vision, such as HSV color space use cases, contour detection, circularity, real-time frame processing, and how to implement them using OpenCV.
I have learned how to use a Raspberry Pi via Linux, SSH remote development, and deploying Python to a Raspberry Pi
I learned how to debug systematically, breaking complex problems into isolated components, testing each independently, and using diagnostic code to identify root causes rather than guessing.

        
