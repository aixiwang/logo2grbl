#-----------------------------------------------------------------------------------------
# LOGO2GRBL -- a command line tool to translate logo instruction to GRBL serial command
#
# Designed by Aixi Wang (aixi.wang@hotmail.com)
#----------------------------------------------------------
# Revision History
#----------------------------------------------------------
# v0.1
# * initial checkin
#-------------------------------------------------------------------------------------------

import math
import sys
import serial
import time

class logo2gcode():
    def __init__(self, fd=sys.stdout,penup_height = 5,pendown_height = -5,arc_min_lenth = 1,ratio=1):
        self.fd = fd
        #set units to millimeters
        self.fd.write("\r\n\r\n")
        time.sleep(2)   # Wait for grbl to initialize 
        self.fd.flushInput()
        self.fd.write("G21\r\n")        
        
        self.x = 0
        self.y = 0
        self.z = 0
        self.heading = 0
        self.penup_height = penup_height
        self.pendown_height = pendown_height
        self.ratio = ratio
        self.is_pen_down = False
        self.arc_min_lenth = arc_min_lenth
        self.up()

    def send_cmd_to_grbl(self,line):
        l = line.strip() # Strip all EOL characters for consistency
        print 'Sending: ' + l,
        self.fd.write(l + '\n') # Send g-code block to grbl
        grbl_out = self.fd.readline() # Wait for grbl response with carriage return
        print ' : ' + grbl_out.strip()
    
    
    def load_file(self,fname):
        f = open(fname, 'r')
        self.lines = f.readlines()
        self.line_cnt = len(self.lines)
        self.i = 0
    
    def changex(self, amt):
        self.setxyz(self.x + amt, self.y, self.z)
 
    def changey(self, amt):
        self.setxyz(self.x, self.y + amt, self.z)

    def setz(self, z):
        self.setxyz(self.x, self.y, z)

    def setxyz(self, x, y, z):
        if x == self.x and y == self.y and z == self.z:
            return
        dist = ((float(x) - self.x) ** 2 + (float(y) - self.y) ** 2 + (float(z) - self.z) ** 2) ** .5
        gcode = "G1 "
        if self.x != x:
            gcode += "X%.3f " % (x * self.ratio)
            self.x = x
        if self.y != y:
            gcode += "Y%.3f " % (y * self.ratio)
            self.y = y
        if self.z != z:
            gcode += "Z%.3f " % (z)
            self.z = z
        gcode += "\r\n"
        
        #print('setxyz gcode:' + str(gcode))
        self.send_cmd_to_grbl(gcode)

    def end(self):
        t.up()
        gcode = "M0"
        self.fd.write(gcode)

    def set_heading(self, heading):
        self.heading = heading
        self.heading %= 360        

    #-------------------------------------------------------------
    # for gcode mapping
    def forward(self, distance):
        new_x = self.x + distance * math.sin(math.radians(self.heading))
        new_y = self.y + distance * math.cos(math.radians(self.heading))
        self.setxy(new_x, new_y)

    def arc(self, angle, r):
        print('arc angle=%f,r=%f' %(angle,r))
        old_pen_down = self.is_pen_down
        old_x = self.x
        old_y = self.y

        start_angle = self.heading
        end_angle = angle + start_angle
        
        if start_angle == angle:
            return
        
        self.up()
        self.forward(r)
        self.down()
        
        while start_angle < end_angle:
            
            new_x = old_x + r * math.sin(math.radians(start_angle%360))
            new_y = old_y + r * math.cos(math.radians(start_angle%360))
            t1 = math.sin(math.radians(start_angle%360))
            t2 = math.cos(math.radians(start_angle%360))
            #print('self.x=%f,self.y=%f,new_x=%f,new_y=%f,r=%f,t1=%f,t2=%f' % (self.x,self.y,new_x,new_y,r,t1,t2)) 
            self.setxy(new_x, new_y)
            start_angle += (float(self.arc_min_lenth* self.ratio)/r)/(2*3.1415926)*360
            #print('start_angle:' + str(start_angle))

        self.up()
        self.setxy(old_x,old_y)
        if old_pen_down == True:
            self.down()
                
    def right(self, angle):
        self.heading += angle
        self.heading %= 360

    def left(self, angle):
        self.heading -= angle
        self.heading %= 360

    def back(self, distance):
        self.forward(-distance)

    def penup(self):
        if self.is_pen_down:
            self.is_pen_down = False
            self.up()

    def pendown(self):
        if not self.is_pen_down:
            self.is_pen_down = True
            self.down()

    def left(self,angle):
        self.set_heading(self.heading - angle)
        
    def right(self,angle):
        self.set_heading(self.heading + angle)

    def up(self):
        self.setz(self.penup_height)

    def down(self):
        self.setz(self.pendown_height)

    def setxy(self, x, y):
        self.setxyz(x, y, self.z)
        
    def sety(self, y):
        self.setxyz(self.x, y, self.z)
        
    def setx(self, x):
        self.setxyz(x, self.y, self.z)
    
    def show_help(self):
        s = '''  
        Supported commands: home,cs,lt,rt,fd,bk,setx,sety,setxy,arc
        Current pos:x=%f,y=%f,z=%f,heading=%f
        ''' % (self.x,self.y,self.z,self.heading)
        print(s)
    #----------------------------------------------------------------
    def translate(self, lines):
        for line in lines:
            #print('line:',line)
            line = line.strip()
            line = line.lower()
            line2 = line.split(' ')

            if line2[0] == 'fd' or line2[0] == 'forward':
                f = float(line2[1].strip())
                self.forward(f)

            elif line2[0] == 'bk' or line2[0] == 'backward':
                f = float(line2[1].strip())
                self.backward(f)

            elif line2[0] == 'left' or line2[0] == 'lt':
                f = float(line2[1].strip())
                self.left(f)

            elif line2[0] == 'right' or line2[0] == 'rt':
                f = float(line2[1].strip())
                self.right(f)

            elif line2[0] == 'setheading' or line2[0] == 'seth':
                f = float(line2[1].strip())
                self.set_heading(f)

            elif line2[0] == 'cs' or line2[0] == 'cleanscreen' or line2[0] == 'home':
                self.setxy(0,0)
                self.heading = 0
                
            elif line2[0] == 'pendown':
                self.pendown()
                
            elif line2[0] == 'penup':
                self.penup()

            elif line2[0] == 'setx':
                f = float(line2[1].strip())
                self.setx(f)

            elif line2[0] == 'sety':
                f = float(line2[1].strip())
                self.sety(f)

            elif line2[0] == 'setxy':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                self.setxy(f1,f2)

            elif line2[0] == 'arc':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                self.arc(f1,f2)

            elif line2[0] == 'help':
                self.show_help()
            
            else:
                print('Invalid command')
                self.show_help()
                
                
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: python logo2grbl.py serial_port up_height down_height arc_min_len')
        sys.exit(1)

    serial_port = sys.argv[1]        
    f1 = float(sys.argv[2])
    f2 = float(sys.argv[3])
    f3 = float(sys.argv[4])
    print('serial_port=%s, up_height=%f, down_height=%f, arc_min_len=%f' %(serial_port,f1,f2,f3))
    
    s = serial.Serial(serial_port,9600)
    t = logo2gcode(s,f1,f2,f3)
    
    while True:
        s = raw_input(':>')
        t.lines = s.split('\n')
        t.translate(t.lines)    

