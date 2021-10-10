#sudo systemctl enable pigpio or sudo pigpiod
#from gpiozero.pins.pigpio import PiGPIOFactory
#from gpiozero             import Servo
from time                 import sleep
import cv2                as cv
import threading          as thr

#pigpioFactory  = PiGPIOFactory("127.0.0.1")
faceCascade    = cv.CascadeClassifier("cascades/face.xml")
eyeCascade     = cv.CascadeClassifier("cascades/eye.xml")
vs             = cv.VideoCapture(0)
camWidth       = int(vs.get(3))
camHeight      = int(vs.get(4))
xMax, xMin     = 0.935, -0.6
xOffset        = 0.14
yMax, yMin     = 0.325, -0.635
yOffset        = -0.084
#servoX         = Servo(pin=27, initial_value=-xOffset, pin_factory=pigpioFactory)
#servoY         = Servo(pin=25, initial_value=-yOffset, pin_factory=pigpioFactory)


def adjustValue(val):
    if(val > 1):
        return 1
    elif(val < -1):
        return -1
    else:
        return val

def threadServo(servo, val):
    servo.value = val
    sleep(1)

'''def moveServos(x, y):
    thr.Thread(target=threadServo, args=(servoX, adjustValue(-((x * (abs(xMax) + abs(xMin) + 1) / camWidth) - 1 + xOffset)))).start()
    thr.Thread(target=threadServo, args=(servoY, adjustValue(-((y * (abs(yMax) + abs(yMin) + 1) / camWidth) - 1 + yOffset)))).start()
    print("Moved servos to:", servoX.value, servoY.value)'''

def exitApp(msg):
    vs.release()
    cv.destroyAllWindows()
    print(msg + " Exiting...")
    exit(-1)

if __name__ == "__main__":
    print("init")
    try:
        while vs.isOpened():
            ret, frame = vs.read()

            if not ret:
                exitApp("Can't receive frame. Is the camera connected?")

            gray = cv.equalizeHist(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))
            
            for (x, y, w, h) in faceCascade.detectMultiScale(gray):
                target = eyeCascade.detectMultiScale(gray[y: y + h, x: x + w])
                
                if len(target) > 0:
                    ex, ey, ew, eh = target[0]
                    targetX, targetY = int(ex + ew/2 + x), int(ey + eh/2 + y)
                    cv.circle(frame, (targetX, targetY), radius = 10, color=(0, 255, 0), thickness = 2)
                    #moveServos(targetX, targetY)
            

            cv.circle(frame, (int(camWidth/2), int(camHeight/2)), radius = 5, color=(255, 0, 0), thickness = 1)
            cv.imshow("Video", frame)
            k = cv.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            '''elif k == ord('w'):
                servoY.value = adjustValue(servoY.value + 0.05)
                print("Servo updated: ", servoX.value, servoY.value)
            elif k == ord('s'):
                servoY.value = adjustValue(servoY.value - 0.05)
                print("Servo updated: ", servoX.value, servoY.value)
            elif k == ord('d'):
                servoX.value = adjustValue(servoX.value + 0.05)
                print("Servo updated: ", servoX.value, servoY.value)
            elif k == ord('a'):
                servoX.value = adjustValue(servoX.value - 0.05)
                print("Servo updated: ", servoX.value, servoY.value)'''
            
        exitApp("Camera disconnected.")
    except KeyboardInterrupt:
        exitApp("Program exited by user.")
        
        

    
