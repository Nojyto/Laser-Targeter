#sudo systemctl enable pigpio or sudo pigpiod
#https://t.ly/QweL
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero             import Servo
from time                 import sleep
import cv2                as cv
import threading          as thr

pigpioFactory    = PiGPIOFactory("127.0.0.1")
servoX           = Servo(pin=27, pin_factory=pigpioFactory)
servoY           = Servo(pin=25, pin_factory=pigpioFactory)
faceCascade      = cv.CascadeClassifier("cascades/face.xml")
eyeCascade       = cv.CascadeClassifier("cascades/eye.xml")
vs               = cv.VideoCapture(-1)
maxX, maxY       = int(vs.get(3)), int(vs.get(4))
midX, midY       = int(maxX / 2) + 20, int(maxY / 2) - 20
red, green, blue = (0, 0, 255), (0, 255, 0), (255, 0, 0)

def exitApp(msg):
    vs.release()
    cv.destroyAllWindows()
    print(msg + " Exiting...")
    exit(-1)

def adjustValue(val):
    if(val > 1):
        return 1
    elif(val < -1):
        return -1
    else:
        return val

def adjustDist(dist, meth):
    val = 0

    if   dist <  50: val = 0.025
    elif dist < 150: val = 0.05
    elif dist < 250: val = 0.10
    elif dist < 500: val = 0.20

    if(meth == "add"):
        return val
    elif(meth == "sub"):
        return -val
    else:
        return "null"
    
def threadServo(servo, val):
    
    '''if servo.value < val:
        while servo.value < val:
            servo.value += 0.01
            sleep(0.01)
    else:
        while servo.value > val:
            servo.value -= 0.01
            sleep(0.01)'''
    servo.value = val
    sleep(0.1)

def moveServos(x, y):
    if x in range(midX - 10, midX + 10) and y in range(midY - 10, midY + 10):
        return

    moveX, moveY = servoX.value, servoY.value

    if   x in range(0, midX - 10):
        moveX += adjustDist(abs(x - midX), "add")
    elif x in range(midX + 10, maxX):
        moveX += adjustDist(abs(x - midX), "sub")

    if   y in range(0, midY - 10):
        moveY += adjustDist(abs(y - midY), "add")
    elif y in range(midY + 10, maxY):
        moveY += adjustDist(abs(y - midY), "sub")

    thr.Thread(target=threadServo, args=(servoX, adjustValue(moveX))).start()
    thr.Thread(target=threadServo, args=(servoY, adjustValue(moveY))).start()
    print("Moved servos to:", adjustValue(moveX), adjustValue(moveY))

if __name__ == "__main__":
    print("init")
    try:
        while vs.isOpened():
            ret, frame = vs.read()

            if not ret:
                exitApp("Can't receive frame. Is the camera connected?")

            gray = cv.equalizeHist(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))
            
            for (x, y, w, h) in faceCascade.detectMultiScale(gray, 1.3, 5):
                target = eyeCascade.detectMultiScale(gray[y: y + h, x: x + w], 1.3, 5)
                if len(target) > 0:
                    ex, ey, ew, eh = target[0]
                    targetX, targetY = int(ex + ew/2 + x), int(ey + eh/2 + y)
                    #cv.circle(frame, (targetX, targetY), 10, green, 2)
                    moveServos(targetX, targetY)

            '''
            cv.circle(frame, (midX, midY), 5, blue, 1)
            cv.rectangle(frame, (midX - 10, midY - 10), (midX + 10, midY + 10), (0, 255, 255), 1)
            cv.rectangle(frame, (0, 0)        , (midX - 10, maxY), red, 1)
            cv.rectangle(frame, (midX + 10, 0), (maxX, maxY)     , red, 1)
            cv.rectangle(frame, (0, 0)        , (maxX, midY - 10), green, 1)
            cv.rectangle(frame, (0, midY + 10), (maxX, maxY)     , green, 1)

            cv.imshow("Video", frame)
            k = cv.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('w'):
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
                print("Servo updated: ", servoX.value, servoY.value)
            '''
            
        exitApp("Camera disconnected.")
    except KeyboardInterrupt:
        exitApp("Program exited by user.")