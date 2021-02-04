from machine import Pin, SPI
import ssd1331
import framebuf
import utime
import math
import mpu6050

# bitmap rgb565 images
import levelFrame
import dot21

# spi initialisation
spi = SPI(0,baudrate=6000000,sck=Pin(6),mosi=Pin(7))
dc=Pin(2,Pin.OUT)
cs=Pin(3,Pin.OUT)

# oled initialisation
width=96
height=64
oled = ssd1331.SSD1331(spi=spi,dc=Pin(2),cs=Pin(3),width=width, height=height)
oled.fill(0)

# frame buffer initialisation

screenArray = bytearray(oled.width * oled.height * 2)
screenFb = framebuf.FrameBuffer(screenArray,
                                oled.width,
                                oled.height,
                                framebuf.RGB565)
screenFb.fill(0)




# build bubble screen

BubbleLevel = levelFrame.levelFrame()


screenFb.blit(BubbleLevel.Fb,0,0)


# the dot
dot = dot21.dot21()



def updateNiveau(levelx, levely, factor):
    screenFb.blit(BubbleLevel.Fb,0,0)
    
    maxRadius = 20.0
    
    centerx = oled.width // 2
    centery = oled.height // 2
    
    # calculate radius
    rx= levelx * factor
    ry= levely * factor
    
    radius = math.sqrt( (rx*rx) + ( ry*ry))
    
    # if radius > maxRadius then correct vector
    if radius > maxRadius:
        factor= maxRadius / radius
        rx = rx * factor
        ry = ry * factor
    
    # correct center of dots
    rx =  rx + centerx - dot.width//2
    ry =  ry + centery - dot.height//2
    
    screenFb.blit(dot.Fb,int(rx),int(ry),0xffff)        
    # ok transfer to screen
    oled.block(0,0,96,64,screenArray)
    
# ok the accelerometer

mpu = mpu6050.MPU6050()
mpu.setSampleRate(200)
mpu.setGResolution(2)

def averageMPU( count, timing_ms):
    gx = 0
    gy = 0
    gz = 0
    gxoffset =  0.07
    gyoffset = -0.04
    for i in range(count):
        g=mpu.readData()
        # offset mpu
        gx = gx + g.Gx - gxoffset
        gy = gy + g.Gy - gyoffset
        gz = gz + g.Gz
        utime.sleep_ms(timing_ms)
    return gx/count, gy/count, gz/count



while True:
    gx, gy, gz = averageMPU(20,5)
    # calculate vector dimension
    vdim = math.sqrt( gx*gx + gy*gy + gz*gz)
           
    # get x angle
    rad2degree= 180 / math.pi
    angleX =  rad2degree * math.asin(gx / vdim)
    angleY =  rad2degree * math.asin(gy / vdim)
    updateNiveau( -angleY, -angleX, 3.0)
            
        
        
