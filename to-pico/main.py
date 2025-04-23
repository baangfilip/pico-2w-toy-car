from do_connect import *
from microdot import Microdot, send_file
from machine import Pin, PWM, ADC
from time import sleep
from microdot.websocket import with_websocket
import _thread

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


light8 = Pin(8, Pin.OUT)
light9 = Pin(9, Pin.OUT)
light9.off()
light8.off()

@app.route('/lights/on')
async def lightson(request):
    light9.on()
    light8.on()
    return 'ok', 200

@app.route('/lights/off')
async def lightsoff(request):
    light9.off()
    light8.off()
    return 'ok', 200

@app.route('/lights/blink')
async def lights(request):
    _thread.start_new_thread(blinklights, ())
    return 'ok', 200

def blinklights():
    for x in range(10):
        light8.on()
        light9.off()
        sleep(0.2)
        light8.off()
        light9.on()
        sleep(0.2)
    light9.off()
    light8.off()
        

@app.route('/ws')
@with_websocket
async def ws(request, ws):
    forward = Pin(11)
    forward_pwm = PWM(forward)
    frequency = 1000
    forward_pwm.freq(frequency)
    while True:
        data = await ws.receive()
        if data == "ping":
            print("pong back")
            await ws.send("pong")
        elif data == "volt":
            voltage = get_vsys()
            print(f'get voltage: {voltage}')
            await ws.send(f'voltage:{voltage}')
        else:
            motorPower = int(data)
            if motorPower > 0 and motorPower < 11:
                if motorPower < 5: 
                    motorPower = 5
                forward_pwm.duty_u16(int(65535/10)*int(motorPower))
                sleep(0.1)
                forward_pwm.duty_u16(0)
                print(f"more than 0 {motorPower}")
            elif motorPower == 0:
                forward_pwm.duty_u16(0)
            else:
                forward_pwm.duty_u16(0)
                print(f"Error occured, value must between -10 and 10 data {data}")

def get_vsys():
    Pin(29, Pin.IN)
    vsys = ADC(29)
    conversion_factor = (3.3 / (65535)) * 3
    return vsys.read_u16()*conversion_factor
try: 
    ip=do_connect()
    if ip is not None:
        app.run(port=80)
except KeyboardInterrupt:
    print("Exception")
