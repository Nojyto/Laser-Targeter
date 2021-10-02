#IMPORTANT: make sure pigpio deamon is running: 'sudo pigpiod'
from flask                import Flask, render_template, Response
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero             import Servo
from time                 import sleep
import cv2                as cv
import threading          as thr


pigpioFactory  = PiGPIOFactory("127.0.0.1")
faceCascade    = cv.CascadeClassifier("cascades/haarcascade_frontalface_alt.xml")
eyeCascade     = cv.CascadeClassifier("cascades/haarcascade_eye.xml")
vs             = cv.VideoCapture(-1)
camWidth       = int(vs.get(3))
camHeight      = int(vs.get(4))
xOffset        = 0
yOffset        = -0.3
servoX         = Servo(pin=27, initial_value=-xOffset, pin_factory=pigpioFactory)
servoY         = Servo(pin=25, initial_value=-yOffset, pin_factory=pigpioFactory)
app            = Flask(__name__)


def adjustValue(val):
    if(val > 1):
        return 1
    elif(val < -1):
        return -1
    else:
        return val

def threadServo(servo, val):
    servo.value = val
    sleep(2)

def moveServos(x, y):
    #servoX.value = adjustValue(-((x * 2 / camWidth) - 1 + xOffset))
    #servoY.value = adjustValue(-((y * 2 / camHeight) - 1 + yOffset))
    threadServoX = thr.Thread(target=threadServo, args=(servoX, adjustValue(-((x * 2 / camWidth) - 1 + xOffset))))
    threadServoY = thr.Thread(target=threadServo, args=(servoY, adjustValue(-((y * 2 / camWidth) - 1 + yOffset))))
    threadServoX.start()
    threadServoY.start()
    print("Moved servos to:")
    print(servoX.value, servoY.value)

def catchEye():
    while True:
        ret, frame = vs.read()

        if not ret:
            print("Can't receive frame. Is the camera connected?")
            break

        gray = cv.equalizeHist(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))

        for (x, y, w, h) in faceCascade.detectMultiScale(frame):
            target = eyeCascade.detectMultiScale(gray[y: y + h, x: x + w])
            
            if len(target) > 0:
                ex, ey, ew, eh = target[0]
                targetX, targetY = int(ex + ew/2 + x), int(ey + eh/2 + y)
                #cv.circle(frame[y: y + h, x: x + w], (targetX, targetY), radius = 10, color=(0, 0, 255), thickness = 2)
                moveServos(targetX, targetY)


def gen_frames():
    while True:
        ret, frame = vs.read()

        if not ret:
            break
        
        ret, buffer = cv.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/move/<servo>/<direc>/<value>")
def posMoveServos(servo, direc, value):
    value = float(value)
    if(servo == "X"):
        if(direc == "pos" and 1 >= servoX.value + value):
            servoX.value += value
        elif(direc == "neg" and -1 <= servoX.value - value):
            servoX.value -= value
    elif(servo == "Y"):
        if(direc == "pos" and 1 >= servoY.value + value):
            servoY.value += value
        elif(direc == "neg" and -1 <= servoY.value - value):
            servoY.value -= value

    return render_template("index.html")

@app.route("/dumpValues")
def dumpValues():
    print("ServoX: ", servoX.value)
    print("ServoY: ", servoY.value)

    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    threadProg = thr.Thread(target=catchEye, args=())
    threadProg.start()
    app.run(host="0.0.0.0", port=80, debug=False)
    vs.release()