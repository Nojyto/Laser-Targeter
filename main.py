import cv2    as cv
from gpiozero import Servo
from time     import sleep


faceCascade = cv.CascadeClassifier("cascades/haarcascade_frontalface_alt.xml")
eyeCascade  = cv.CascadeClassifier("cascades/haarcascade_eye.xml")
vs          = cv.VideoCapture(0)
servoX      = Servo(25)
servoY      = Servo(27)


def moveServo(x, y):
    sleep(0.5)

def exitApp(msg):
    print(msg + " Exiting...")
    vs.release()
    cv.destroyAllWindows()
    exit(-1)

if __name__ == "__main__":
    if not vs.isOpened():
        exitApp("Can't open camera.")
    
    '''servoX.mid()
    servoY.mid()'''

    try:
        while True:
            ret, frame = vs.read()

            if not ret:
                exitApp("Can't receive frame (stream end?).")

            gray = cv.equalizeHist(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))

            for (x, y, w, h) in faceCascade.detectMultiScale(frame):
                roi_gray   = gray [y: y + h, x: x + w]
                #roi_color = frame[y: y + h, x: x + w]
                #cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                target = eyeCascade.detectMultiScale(roi_gray)
                
                if len(target) > 0:
                    ex, ey, ew, eh = target[0]
                    xTarget, yTarget = int(ex + ew/2 + x), int(ey + eh/2 + y)
                    moveServo(xTarget, yTarget)
                    print(xTarget, yTarget)
                    #cv.circle(roi_color, (xTarget, yTarget), radius = 10, color=(0, 0, 255), thickness = 2)

            '''
            cv.imshow("Video", frame)
            if cv.waitKey(1) == 27:
                exitApp("Keyboard Interrupt.")
            '''

    except KeyboardInterrupt:
        exitApp("Keyboard Interrupt.")


#scp main.py pi@192.168.1.68:/home/pi/LaserTargeter/