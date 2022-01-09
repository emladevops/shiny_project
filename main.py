### FCTC0230 - Trần Trọng Nghĩa - Final Project ###
from bmp180 import BMP180
from uthingsboard.client import TBDeviceMqttClient
from machine import I2C, Pin, PWM, Timer, ADC
import network,time,urequests,json,uping
beeper = PWM(Pin(18), freq=0, duty=0)
def pingTest(ip):
    try:
        uping.ping(str(ip), 1, quiet=True)
        return('success')
    except:
        return('fail')
def buzzerTrigger(status):
    status2 = status
    if status2 == 'on':
        beeper = PWM(Pin(18), freq=5, duty=512)
    if status2 == 'off':
        beeper = PWM(Pin(18), freq=0, duty=0)
def on_server_side_rpc_request(request_id, method, request_body):
    if '0' in str(request_body):
        buzzerTrigger('off')
    if '1' in str(request_body):
        buzzerTrigger('on')
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('TP-Link_598E','79961202')
time.sleep(5)
client = TBDeviceMqttClient('tb.schacweb.com', access_token='THISISAINVALIDTOKEN')
print('Connecting...')
client.set_server_side_rpc_request_handler(on_server_side_rpc_request)
client.connect()
print('Getting ready to print out result of the BMP180 ;)')
class LDR:
    def __init__(self, pin, min_value=0, max_value=100):
        if min_value >= max_value:
            raise Exception('Min value is greater or equal to max value')
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.min_value = min_value
        self.max_value = max_value
    def read(self):
        return self.adc.read()
    def value(self):
        return (self.max_value - self.min_value) * self.read() / 4095
ldr = LDR(34)
while True:
    if sta_if.isconnected() == False:
        sta_if.connect('TP-Link_598E','79961202')
        client.connect()
    if pingTest('tb.schacweb.com') == 'success':
        locationinfo = urequests.get('http://ipinfo.io/json?token=1bb503ca7e3a8a').json()
        ip = locationinfo['ip']
        loc = locationinfo['loc'].split(",")
        try:
            value=ldr.value()
            result = '{}'.format(value)
        except:
            value = 0
            result = 0
        try:
            bus =  I2C(scl=Pin(4), sda=Pin(5), freq=100000)
            bmp180 = BMP180(bus)
            bmp180.oversample_sett = 2
            bmp180.baseline = 101325
            temp = bmp180.temperature
            p = bmp180.pressure
            altitude = bmp180.altitude
        except:
            temp = 0
            p = 0
            altitude = 0 
        telemetry = {"temperature": temp, "humidity": 20, "pressure": p, "light": result,'enabled': True, 'latitude': loc[0], 'longitude': loc[1], "altitude": altitude}
        time.sleep(0.5)
        client.check_msg()
        client.send_telemetry(telemetry)
    if pingTest('tb.schacweb.com') == 'fail':
        client.connect()
