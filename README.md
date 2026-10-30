Tennis ball collecting robot...

Purpose: An autonomous robot that uses computer vision to gather tennis balls

As a competitive tennis player, I decided to try to ease the tedious task of picking up tennis balls that are scattered around the court

Current Status: Ball can identify and drive towards a ball, and capture within frame connected to servo however this is inconsistent. Help of AI to get video streaming working.

Hardware: Raspberry Pi 4
          Pi Cam 3
          L298n motor driver
          3.4V-7V DC Motors and wheels kit
          9V Rechargeable Lithium-Ion battery
          5V buck converter
          5V portable power bank
          3D printed car body with threaded inserts
          servo

key Decisions:

          Using YOLO over HSV Colour Masking
          NCNN as it is optimized for ARM processor
          Run detection every second frame:

                    if frame_count % 2 == 0:
                        best_area = 0
                        results = model(frame, verbose=False)

          Identify closest ball using area:

                    area = (x2 - x1) * (y2 - y1)
                    if area > best_area:
                        best_area = area
                        best_box = (x1, y1, x2, y2)

          Using ball's position on camera to determine steering:

                    def adjust(cx):
                        global direction
                        limit_low = 60
                        limit_high = 260
          
                        if cx < limit_low:
                            if direction != "left":
                                direction = "left"
                                stop()
                                time.sleep(1)       
                            else:
                                left(70)
                                time.sleep(0.2)     
                                stop()             
                        elif cx > limit_high:
                                      
                        elif 10000 >= best_area >= 1000:
                            forward(60)             
                        else:
                            forward(100)


          Triggering servo trap:

                    if best_area >= 9350 and 100 < cx < 220:      
                        stop()
                        set_angle(5)                              
                    elif best_area >= 20000:                      
                        stop()
                        set_angle(5)
                    else:
                        adjust(cx)

              







VIDEO OF PROGRESS SO FAR!

https://youtube.com/shorts/8FeY7tgTsZA?feature=share
        
