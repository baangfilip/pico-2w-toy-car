from do_connect import *
from microdot import Microdot, send_file
import ssl
from machine import Pin, PWM, ADC
from time import sleep
from microdot.websocket import with_websocket
import _thread

app = Microdot()

@app.route('/')
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
    #blinklights()
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

def start_web_server(): 
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslctx.load_cert_chain('cert.der', 'key.der')
    app.run(port=4443, debug=True, ssl=sslctx)

try: 
    ip=do_connect()
    for x in range(10):
        light8.on()
        light9.on()
        sleep(0.1)
        light8.off()
        light9.off()
        sleep(0.1)
    if ip is not None:
        print("starting web server")
        start_web_server()
except KeyboardInterrupt:
    print("Exception")