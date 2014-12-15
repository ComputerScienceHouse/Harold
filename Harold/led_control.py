import RPi.GPIO as GPIO


def open_pins():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(7, True)
    GPIO.output(11, True)
    print "GPIO Init"


def on(switch):
    if switch:
        GPIO.output(7, True)
        GPIO.output(11, True)
        print "LED ON"
    elif not switch:
        GPIO.output(7, False)
        GPIO.output(11, False)
        print "LED OFF"


def cleanup():
    GPIO.cleanup()