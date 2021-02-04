import ustruct
import utime
from micropython import const

_DRAWLINE = const(0x21)
_DRAWRECT = const(0x22)
_NO_SCROLL = const(0x2e)
_FILL = const(0x26)
_PHASEPERIOD = const(0x12)
_SETCOLUMN = const(0x15)
_SETROW = const(0x75)
_CONTRASTA = const(0x81)
_CONTRASTB = const(0x82)
_CONTRASTC = const(0x83)
_MASTERCURRENT = const(0x87)
_SETREMAP = const(0xA0)
_STARTLINE = const(0xA1)
_DISPLAYOFFSET = const(0xA2)
_NORMALDISPLAY = const(0xA4)
_DISPLAYALLON = const(0xA5)
_DISPLAYALLOFF = const(0xA6)
_INVERTDISPLAY = const(0xA7)
_SETMULTIPLEX = const(0xA8)
_SETMASTER = const(0xAD)
_DISPLAYOFF = const(0xAE)
_DISPLAYON = const(0xAF)
_POWERMODE = const(0xB0)
_PRECHARGE = const(0xB1)
_CLOCKDIV = const(0xB3)
_PRECHARGEA = const(0x8A)
_PRECHARGEB = const(0x8B)
_PRECHARGEC = const(0x8C)
_PRECHARGELEVEL = const(0xBB)
_VCOMH = const(0xBE)
_LOCK = const(0xfd)


class SSD1331:

    _INIT = (
        (_DISPLAYOFF, b''),
        (_LOCK, b'\x0b'),
        (_SETREMAP, b'\x72'), # RGB Color
        (_STARTLINE, b'\x00'),
        (_DISPLAYOFFSET, b'\x00'),
        (_NORMALDISPLAY, b''),
        (_PHASEPERIOD, b'\x31'),
        (_SETMULTIPLEX, b'\x3f'),
        (_SETMASTER, b'\x8e'),
        (_POWERMODE,b'\x0b'),
        (_PRECHARGE, b'\x31'), #;//0x1F - 0x31
        (_CLOCKDIV, b'\xf0'),
        (_VCOMH, b'\x3e'), #;//0x3E - 0x3F
        (_MASTERCURRENT, b'\x0c'), # ;//0x06 - 0x0F
        (_PRECHARGEA, b'\x64'),
        (_PRECHARGEB, b'\x78'),
        (_PRECHARGEC, b'\x64'),
        (_PRECHARGELEVEL, b'\x3a'), # 0x3A - 0x00
        (_CONTRASTA, b'\x91'), #//0xEF - 0x91
        (_CONTRASTB, b'\x50'), #;//0x11 - 0x50
        (_CONTRASTC, b'\x7d'), #;//0x48 - 0x7D
        (_NO_SCROLL, b''),
        (_DISPLAYON, b'')
    )
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">BB"
    _ENCODE_LINE = ">BBBBBBB"
    _ENCODE_RECT = ">BBBBBBBBBB"

    def line(self,x1,y1,x2,y2,color):
        r= (color >> 10) & 0x3e
        g= (color >> 5) & 0x3e
        b= (color & 0x1f) << 1
        data =ustruct.pack(self._ENCODE_LINE,x1,y1,x2,y2,r,g,b)
        self._write(_DRAWLINE,data)

    def rectangle(self,x,y,width,height,linecolor,fillcolor):
        if fillcolor is None:
          self._write(_FILL,b'\x00')
          br = 0
          bg = 0
          bb = 0
        else:
          self._write(_FILL,b'\x01')
          br= (fillcolor >> 10) & 0x3e
          bg= (fillcolor >> 5) & 0x3e
          bb= (fillcolor & 0x1f) << 1
        r= (linecolor >> 10) & 0x3e
        g= (linecolor >> 5) & 0x3e
        b= (linecolor & 0x1f) << 1
        data = ustruct.pack(self._ENCODE_RECT,x,y,x+width-1,y+height-1,r,g,b,br,bg,bb)
        self._write(_DRAWRECT,data)


    def fill(self,color=0):
        self.rectangle(0,0,self.width,self.height,color,color)


    def __init__(self, spi, dc, cs, rst=None, width=96, height=64):
        self.spi=spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.width = width
        self.height = height
        self.reset()
        for command,data in self._INIT:
           self._write(command,data)
        self.font = None

    def _write(self, command=None, data=None):
        if command is None:
            self.dc.value(1)
        else:
            self.dc.value(0)
        self.cs.value(0)
        if command is not None:
            self.spi.write(bytearray([command]))
        if data is not None:
            self.spi.write(data)
        self.cs.value(1)


    def _read(self, command=None, count=0):
        self.dc.value(0)
        self.cs.value(0)
        if command is not None:
            self.spi.write(bytearray([command]))
        if count:
            data = self.spi.read(count)
        self.cs.value(1)
        return data


    def color565(self,r, g, b):
        #  5  4  3  2  1  0  9  8  7  6  5  4  3  2  1  0
        #  R4 R3 R2 R1 R0 G5 G4 G3 G2 G1 G0 B4 B3 B2 B1 B0
        # return  (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3
        
        #  for ARM need  to swap byte
        #  G2 G1 G0 B4 B3 B2 B1 B0 R4 R3 R2 R1 R0 G5 G4 G3
        return  (g & 0x1C) << 1 | (b >> 3) | (r & 0xf8) | g >> 5


    def pixel(self, x , y , color=None):
        """ set pixel position """
        self._write(_SETCOLUMN,bytearray([x,x]))
        self._write(_SETROW,bytearray([y,y]))

        if color is None:
          """ read pixel """
          return self._read(None,2)
        else:
#          self._write(None,bytearray([color >> 8, color &0xff]))
          self.line(x,y,x,y,color)

    def block(self, x,y,width,height, data):
        self._write(_SETCOLUMN, bytearray([x,x+width-1]))
        self._write(_SETROW,bytearray([y,y+height-1]))
        self._write(None,data)

    def reset(self):
      if self.rst is not None:
         self.rst.value(0)
         utime.sleep(0.1)
         self.rst.value(1)

    def setFont(self,font):
      self.font= font

    def putChar (self,x,y, utf8Char, color):
       #print("putChar(x={},y={},c={},color={})".format(x,y,utf8Char,color))
       if self.font is None:
          return x
    # {offset, width, height, advance cursor, x offset, y offset} */
       self.font.setPosition(utf8Char)
       _offset,_width,_height,_cursor,x_off,y_off =  self.font.current_glyph
       #print("_offset",_offset)
       #print("Width",_width)
       #print("height",_height)
       #print("cursor",_cursor)
       #print("xoff",x_off)
       #print("yoff",y_off)
       for y1 in range(_height):
         for x1 in range(_width):
              if self.font.getNext():
                 self.pixel(x+x1+x_off,y+y1+y_off,color)
       return x+_cursor

    def putText(self,x,y,txt,color):
      if not self.font is None:
        for  c in txt:
          x = self.putChar(x,y,c,color)
          
          
if __name__ == "__main__":
    from machine import Pin, SPI
    spi = SPI(0,baudrate=10000000,sck=Pin(6),mosi=Pin(7))
    dc=Pin(2,Pin.OUT)
    cs=Pin(3,Pin.OUT)
    oled = SSD1331(spi=spi,dc=Pin(2),cs=Pin(3))
    oled.fill(0)

    import framebuf
    buffer = bytearray(oled.width * oled.height * 2)
    fb = framebuf.FrameBuffer(buffer,
                              oled.width,
                              oled.height,
                              framebuf.RGB565)

    #test frame buffer
    colors = []
    for i in range(8):
        r = (i & 1) * 255
        g = ((i >> 1)  & 1)  * 255
        b = ((i >> 2) & 1 ) * 255
        colors.append(oled.color565(r,g,b))
            
    while True:
        for color in colors:
            fb.fill(color)
            oled.block(0,0,96,64,buffer)
            utime.sleep(1)
        