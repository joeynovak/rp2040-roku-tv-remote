import machine
import time

p1 = machine.Pin(1)
pwm1 = machine.PWM(p1)
pwm1.duty_u16(32000)
pwm1.freq(38000)

bluePin = machine.Pin(20, machine.Pin.OUT)

volDownControl = 16
volUpControl = 15
powerToggleControl = 23

leftControl = 30
rightControl = 45
upControl = 25
downControl = 51
okControl = 42

backControl = 102
homeControl = 3

class NEC:
    def __init__(self, deviceId, subDeviceId):
        self.deviceId = deviceId
        self.subDeviceId = subDeviceId
        
    def delay_us(self, i):
        #Correction factor
        i=round(i*0.89, 0);
        startTime = time.ticks_us()
        while time.ticks_us() - startTime < i:
            pass
        
    def sendSignalStart(self):
        self.sendPulses()
        self.delay_us(9 * 1000)
        self.stopPulses()
        self.delay_us(4500)
        
    def sendSignal0(self):
        self.sendPulses()
        self.delay_us(562)
        self.stopPulses()
        self.delay_us(563)
        
    def sendSignal1(self):
        self.sendPulses()
        self.delay_us(562)
        self.stopPulses()
        self.delay_us(1687)
        
    def sendControl(self, controlData):
        print(str(controlData))
        self.sendSignalStart()
        self.sendByte(self.deviceId)
        self.sendByte(self.subDeviceId)
        self.sendByte(controlData)
        self.sendByte(~controlData)
        self.sendSignal1()
        bluePin.value(1)
        self.delay_us(200000)
        
    def sendByte(self, data):
        for i in range(0,8):
            bit = (data & 1)
            if bit == 0:
                self.sendSignal0()
            else:
                self.sendSignal1()
            data = data>>1    
        
    def sendPulses(self):
        bluePin.value(1)
        pwm1.duty_u16(32000)
        
    def stopPulses(self):
        bluePin.value(0)
        pwm1.duty_u16(0)
        
device = NEC(234, 199)
device.sendPulses()

MAX = 65535
MIDDLE = MAX/2
ENDSLOP = 1000
DEADZONE = 10000

print(str(MIDDLE))


while 1:
    up = False
    middle = True
    down = False
    left = False
    center = True
    right = False
    click = False
    
    jy = machine.ADC(machine.Pin(26)).read_u16()
    jx = machine.ADC(machine.Pin(27)).read_u16()
    clickValue = machine.ADC(machine.Pin(28)).read_u16()
        
    if(jy > MAX - ENDSLOP):
        up = True
        
    if(jy < ENDSLOP):
        down = True
        
    if(jy < MIDDLE - DEADZONE or jy > MIDDLE + DEADZONE):
        middle = False
        
    if(jx > MAX - ENDSLOP):
        right = True
        
    if(jx < ENDSLOP):
        left = True
        
    if(jx < MIDDLE - DEADZONE or jx > MIDDLE + DEADZONE):
        center = False

    if(clickValue < 1000):
        click = True
        
    #Volume Down
    if(up and left):
        device.sendControl(volDownControl)
        
    if(up and right):
        device.sendControl(volUpControl)
        
    if(down and left):
        device.sendControl(backControl)
    
    if(down and right):
        device.sendControl(homeControl)
        
    if(down and center):
        device.sendControl(downControl)
        
    if(up and center):
        device.sendControl(upControl)
        
    if(left and middle):
        device.sendControl(leftControl)
        
    if(right and middle):
        device.sendControl(rightControl)
        
    
        
    if(up and click):
        device.sendControl(powerToggleControl)
        
    if(click and center and middle):
        device.sendControl(okControl)
            
    
    time.sleep_ms(50)
    
    