#-----------------------------------------------------------------------------------------
# LOGO2GRBL -- a command line tool to translate logo instruction to GRBL serial command
#
# Designed by Aixi Wang (aixi.wang@hotmail.com)
#----------------------------------------------------------
# Revision History
#----------------------------------------------------------
# v0.1
# * initial checkin
# v0.2
# * added setuph,setdownh,reset command support
# v0.3
# * added rect command
# * added gcode_save_to_file parameter (you can reivew generated gcode.txt with http://jherrm.com/gcode-viewer/)
# * added serial emulation mode support when no available serial port exits
# v0.4
# * added pocketrect,pocketarc command
# v0.5
# * changed pocketrect,pocketarc name to prect & parc
# * redefined rect and prect function
# * added BATCH mode support
# * added comment support('#')
# v0.6
# * added feedrate init
# * fixed rect, prect direction issue
# * added feedrate command
# * fixed multiple blankspace issue
# v0.7
# * added rungcode command
# * added send_cmd_to_grbl response checking
# v0.8
# * added e,c,s,f command
# * added manual training & log function
# v0.8
# * added e,c,s,f command
# * added manual training & log function
# v0.9
# * added w,r command
# * fixed 'ok' error
# v0.10
# * fixed penup issue
# * removed initial penup command
# * updated $6 parameter for io adaptor board
#-------------------------------------------------------------------------------------------

import math
import sys
import serial
import time

run_mode = 'CLI'
global run_mode

class logo2gcode():
    def __init__(self, fd=sys.stdout,penup_height = 5,pendown_height = -5,arc_min_lenth = 1,ratio=1, gcode_save_to_file = True):
        global run_mode    
        self.fd = fd
        self.gcode_fd = None
        self.logo_fd = None
        self.write_logo_flag = False
        #set units to millimeters
        if gcode_save_to_file:
            gcode_fd = open('gcode.txt','w')
            self.gcode_fd = gcode_fd
            self.write_gcode("\r\n\r\n")

        if run_mode == 'CLI':
            logo_fd = open('logo_manual.txt','w')
            self.logo_fd = logo_fd

            
        time.sleep(2)   # Wait for grbl to initialize
        try:
            self.fd.flushInput()
        except:
            print('Flush gcode_fd exception.')
            pass
        self.write_gcode("G21\r\n")

        # It's for my CNC, please update it
        self.send_cmd_to_grbl("$0=80")
        self.send_cmd_to_grbl("$1=266.6666")
        self.send_cmd_to_grbl("$2=160")
        # init feedrate
        self.send_cmd_to_grbl("$4=120")
        # b7 -- z dir, b6 -- y dir, b5 -- x dir
        self.send_cmd_to_grbl("$6=223")
        
        
        self.x = 0
        self.y = 0
        self.z = 0
        self.heading = 0
        self.penup_height = penup_height
        self.pendown_height = pendown_height
        self.ratio = ratio
        self.is_pen_down = False
        self.arc_min_lenth = arc_min_lenth
        #self.up()
    
    def write_gcode(self,gcode):
        print 'Sending: ' + gcode
        if self.gcode_fd != None and gcode[0] != '$' and gcode != '\r\n' and gcode != '\r' and gcode != '\n':
            self.gcode_fd.write(gcode)
            self.gcode_fd.flush()
        
        if self.fd != None:
            self.fd.write(gcode)
            self.fd.flush()

    def write_logo(self,logo_code):        
        if self.logo_fd != None:
            self.logo_fd.write(logo_code + '\r\n')
            self.logo_fd.flush()
            
    def send_cmd_to_grbl(self,line):
        l = line.strip() # Strip all EOL characters for consistency  
        self.write_gcode(l + '\n') # Send g-code block to grbl
        
        if self.fd != None:
            grbl_out = self.fd.readline() # Wait for grbl response with carriage return
            print 'grbl_out:',grbl_out
            grbl_out = grbl_out.lower()
            if grbl_out.strip() == 'ok':
                print ' : ' + grbl_out.strip()
            else:
                print('invalid response')
                s = raw_input('any key to continue or ctr + c to exit!')

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
        self.send_cmd_to_grbl(gcode)

    def set_heading(self, heading):
        self.heading = heading
        self.heading %= 360        

        
    #-------------------------------------------------------------
    # for gcode mapping
    def forward(self, distance):
        new_y = self.y + distance * math.cos(math.radians(self.heading))
        new_x = self.x + distance * math.sin(math.radians(self.heading))
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

    def rect(self,x_delta,y_delta):
        print('rect x_delta=%f,y_delta=%f' %(x_delta,y_delta))
        old_pen_down = self.is_pen_down
        old_x = self.x
        old_y = self.y
        old_heading = self.heading
        
        self.down()
        self.forward(y_delta)
        self.right(90)
        self.forward(x_delta)
        self.right(90)
        self.forward(y_delta)
        self.right(90)
        self.forward(x_delta)

        self.up()
        self.setx(old_x)
        self.sety(old_y)
        self.set_heading(old_heading)
        
        if old_pen_down == True:
            self.down()
        else:
            self.up()

    def pocketrect(self,x_delta,y_delta,step_x,step_y):
        old_x = self.x
        old_y = self.y
        old_heading = self.heading
        self.up()
        
        new_delta_x = x_delta
        new_delta_y = y_delta
        
        if x_delta == 0 or y_delta == 0:
            print('invalid x_delta or y_delta value')
            return
            
        if x_delta > 0:
            step_x2 = abs(step_x)
        else:
            step_x2 = (-1)*abs(step_x)
            
        if y_delta > 0:
            step_y2 = abs(step_y)
        else:
            step_y2 = (-1)*abs(step_y)
        
        while True:
            self.rect(new_delta_x,new_delta_y)

            self.up()
            #self.setxy(self.x + step_x2,self.y + step_y2)        
            self.forward(step_y2)
            self.right(90)
            self.forward(step_x2)
            self.left(90)
            
            flag1 = 0
            if x_delta > 0 and new_delta_x <= 0:
                flag1 += 1
                
            elif x_delta < 0 and new_delta_x >= 0:
                flag1 += 1
            
            else:
                new_delta_x -= step_x2*2
            
            if y_delta > 0 and new_delta_y <= 0:
                flag1 += 1

            elif y_delta < 0 and new_delta_y >= 0:
                flag1 += 1
            else:
                new_delta_y -= step_y2*2
            
            if flag1 >= 1:
                break
            
        self.setxy(old_x,old_y)
        self.set_heading(old_heading)
        
    def pocketarc(self,angle,r,step_r):
        old_x = self.x
        old_y = self.y
        old_heading = self.heading
        self.up()
        
        new_r = r
        new_x = self.x
        new_y = self.y
        
        if angle <= 0 or step_r <= 0 or r <= 0:
            print('invalid parameter')
            return
            
        while True:
            self.arc(angle,new_r)
            new_r = new_r - step_r*2
            if (new_r) <= 0:
                break
            
        self.setxy(old_x,old_y)
        
    def right(self, angle):
        self.heading += angle
        self.heading %= 360

    def left(self, angle):
        self.heading -= angle
        self.heading %= 360

    def back(self, distance):
        self.forward(-distance)

    def penup(self):
        self.up()

    def pendown(self):
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

    def feedrate(self, x):
        s = '$4=' + str(x)
        self.send_cmd_to_grbl(s)
        
    def show_help(self):
        s = '''  
cmd list: penup,pendown,home,cs,lt,rt,fd,bk,setx,sety,setz,setxy,arc,setuph,setdownh,reset,rect,prect,parc,feedrate,e,c,s,f,w,r,rungcode
Current pos:x=%f,y=%f,z=%f,heading=%f
        ''' % (self.x,self.y,self.z,self.heading)
        print(s)
    #----------------------------------------------------------------
    def translate(self, lines):
        global run_mode
        
        for line in lines:
            #print('line:',line)
            if line[0] == '#':
                continue
            
            line = line.replace('\t',' ')
            
            last_lens = len(line)
            new_lens = last_lens
            while True:                
                line = line.replace('  ',' ')
                last_lens = new_lens
                new_lens = len(line)
                #print(last_lens,new_lens)
                if last_lens == new_lens:
                    break
                    
            line = line.lower()
            line = line.rstrip('\r')
            line = line.rstrip('\n')
            line = line.rstrip('\r\n')
            

            line2 = line.split(' ')


            self.write_logo_flag = True                
            
            if line2[0] == 'fd' or line2[0] == 'forward':
                f = float(line2[1].strip())
                self.forward(f)
                
            elif line2[0] == 'bk' or line2[0] == 'backward':
                f = float(line2[1].strip())
                self.back(f)

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
                self.penup()
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
                
            elif line2[0] == 'setz':
                f = float(line2[1].strip())
                self.setz(f)
                
            elif line2[0] == 'setxy':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                self.setxy(f1,f2)
                
            elif line2[0] == 'arc':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                self.arc(f1,f2)
                
            elif line2[0] == 'rect':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                self.rect(f1,f2)
                
            elif line2[0] == 'prect':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                f3 = float(line2[3].strip())
                f4 = float(line2[4].strip())                
                self.pocketrect(f1,f2,f3,f4)
                
            elif line2[0] == 'parc':
                f1 = float(line2[1].strip())
                f2 = float(line2[2].strip())                
                f3 = float(line2[3].strip())               
                self.pocketarc(f1,f2,f3)                
                
            elif line2[0] == 'reset':
                self.x = 0
                self.y = 0
                self.z = 0
                
            elif line2[0] == 'setuph':
                f = float(line2[1].strip())
                self.penup_height = f
                
            elif line2[0] == 'setdownh':
                f = float(line2[1].strip())
                self.pendown_height = f
                
            elif line2[0] == 'feedrate':
                f = float(line2[1].strip())
                self.feedrate(f)
                
            elif line2[0] == 'rungcode':
                s = str(line2[1].strip())
                f = open(s,'r')
                lines = f.readlines()
                print('rungcode started!')
                
                for line in lines:
                    self.send_cmd_to_grbl(line)       
                print('rungcode done!')

            elif line2[0] == 'e':
                # y += 0.5
                self.setxy(self.x,self.y + 0.5)
                
            elif line2[0] == 'c':
                # y -= 0.5
                self.setxy(self.x,self.y - 0.5)                
            elif line2[0] == 's':
                # x -= 0.5
                self.setxy(self.x - 0.5,self.y)
            elif line2[0] == 'f':
                # x += 0.5
                self.setxy(self.x + 0.5,self.y)

            elif line2[0] == 'w':
                # x += 0.5
                self.setz(self.z + 0.5)

            elif line2[0] == 'r':
                # x += 0.5
                self.setz(self.z - 0.5)
                
            elif line2[0] == 'help':
                self.show_help()

            else:
                print('Invalid command:' + str(line2))
                self.show_help()
                self.write_logo_flag = False

            if run_mode == 'CLI' and self.write_logo_flag == True:
                #print 'run_mode:',run_mode,' logo_code:',line
                self.write_logo(line)
            
            

if __name__ == '__main__':
    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print('Usage: python logo2grbl.py CLI serial_port up_height down_height arc_min_len')
        print('Usage: python logo2grbl.py BATCH script_file serial_port up_height down_height arc_min_len')
        sys.exit(1)

    run_mode = sys.argv[1]
    if run_mode == 'CLI' and len(sys.argv) == 6:
        serial_port = sys.argv[2]
        f1 = float(sys.argv[3])
        f2 = float(sys.argv[4])
        f3 = float(sys.argv[5])
        print('CLI mode,serial_port=%s, up_height=%f, down_height=%f, arc_min_len=%f' %(serial_port,f1,f2,f3))

    elif run_mode == 'BATCH' and len(sys.argv) == 7:
        script_file = sys.argv[2]
        serial_port = sys.argv[3]
        f1 = float(sys.argv[4])
        f2 = float(sys.argv[5])
        f3 = float(sys.argv[6])
        print('BATCH mode,serial_port=%s, up_height=%f, down_height=%f, arc_min_len=%f' %(serial_port,f1,f2,f3))
    
    try:
        s = serial.Serial(serial_port,9600)
        t = logo2gcode(s,f1,f2,f3,True)
    except:
        print('open serial fail! enable emulation mode')
        t = logo2gcode(None,f1,f2,f3,True)
    
    if run_mode == 'CLI':
        while True:
            s = raw_input(':>')
            t.lines = s.split('\n')
            try:
                t.translate(t.lines)
            except Exception as e:
                print('Invalid command line, exception:' + str(e))
                t.show_help()
                
    else:
        f = open(script_file,'r')
        t.lines = f.readlines()
        try:
            t.translate(t.lines)
        except Exception as e:
            print('Invalid command line, exception:' + str(e))
            t.show_help()
