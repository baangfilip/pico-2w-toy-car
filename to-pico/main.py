from do_connect import *
from microdot import Microdot, send_file
from machine import Pin, PWM
from time import sleep
from microdot.websocket import with_websocket

app = Microdot()

@app.route('/hello')
async def index(request):
    return send_file('index.html')

@app.route('/assets/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('assets/' + path, max_age=86400)

@app.route('/ws')
@with_websocket
async def ws(request, ws):
    forward = Pin(11)
    forward_pwm = PWM(forward)
    backward = Pin(10)
    backward_pwm = PWM(backward)
    frequency = 1000
    forward_pwm.freq(frequency)
    backward_pwm.freq(frequency)
    while True:
        data = await ws.receive()
        motorPower = int(data)
        if motorPower > 0 and motorPower < 11:
            forward_pwm.duty_u16(int(30000/10)*int(motorPower))
            sleep(0.1)
            forward_pwm.duty_u16(0)
            print(f"more than 0 {motorPower}")
        elif motorPower < 0 and motorPower > -11:
            backward_pwm.duty_u16(int(30000/10)*int(motorPower*-1))
            sleep(0.1)
            backward_pwm.duty_u16(0)
            print(f"less than 0 {motorPower}")
        elif motorPower == 0:
            backward_pwm.duty_u16(0)
            forward_pwm.duty_u16(0)
        else:
            backward_pwm.duty_u16(0)
            forward_pwm.duty_u16(0)
            print(f"Error occured, value must between -10 and 10 data {data}")
    led_pwm.deinit()

try: 
    ip=do_connect()
    if ip is not None:
        app.run(port=80)
except KeyboardInterrupt:
    print("Exception")
