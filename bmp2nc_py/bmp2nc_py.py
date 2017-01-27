#--------------------------------------------------
# BMP2NC_PY
# Convert bmp file to NC code (python version)
# aixi.wang@hotmail.com
#---------------------------------------------------
from bmpy import *
import time
import math

# 5mm
z_safe_height = 3
# -5mm
z_drill_height = -3
# > jump_distance, move to high, move to target position, then start to drill 
jump_distance = 1
    

#------------------------------
# help
#------------------------------
def help():
    print "Usage: " + sys.argv[0] + " bmp_filename x_mm  [r g b][z_safe z_drill]"
    print 'example 1: python bmp2nc.py d.bmp 5'
    print 'example 2: python bmp2nc.py d.bmp 255 0 0'
    print 'example 2: python bmp2nc.py d.bmp 255 0 0 5 -5'
    
#------------------------------
# distance_p2p
#------------------------------
def distance_p2p(x1,y1,x2,y2,mm_per_pt):
    return math.sqrt((x1-x2)*(x1-x2)*mm_per_pt*mm_per_pt + (y1-y2)*(y1-y2)*mm_per_pt*mm_per_pt)
    
if __name__ == "__main__":

    mm_per_pt = 0
    if len(sys.argv) == 3:
        image_name = sys.argv[1]
        x_mm = float(sys.argv[2])
        
        draw_r = 0
        draw_g = 0
        draw_b = 0

    elif len(sys.argv) == 6:
        image_name = sys.argv[1]
        x_mm = float(sys.argv[2])
        
        draw_r = int(sys.argv[3])
        draw_g = int(sys.argv[4])
        draw_b = int(sys.argv[5])
        
    elif len(sys.argv) == 8:
        image_name = sys.argv[1]
        x_mm = float(sys.argv[2])
        
        draw_r = int(sys.argv[3])
        draw_g = int(sys.argv[4])
        draw_b = int(sys.argv[5])
    
        z_safe_height = float(sys.argv[6])
        z_drill_height = float(sys.argv[7])
        
    else:
        help()
        sys.exit(1)


    bmp = BMPy(image_name)
    #bmp.draw_line( (0x00,0x00,0x00),0,0,20,30)

    x_min = bmp.width-1
    x_max = 0
    
    #
    # make picture points become black & white
    #
    for x in xrange(bmp.width):
        for y in xrange(bmp.height):
            (r,b,g) = bmp.bitmap[y][x]
            
            #if r > 128:
            if (r == draw_r) and (g == draw_g) and (b == draw_b):
                bmp.bitmap[y][x] = (0,0,0)
                if x < x_min:
                    x_min = x
                if x > x_max:
                    x_max = x 
                    
            else:
                bmp.bitmap[y][x] = (255,255,255)
               
    
    #
    # caculate ?mm/point
    #
    mm_per_pt = x_mm/(x_max-x_min)
    #print 'x_mm:',x_mm        
    #print 'x_min:',x_min
    #print 'x_max:',x_max       
    #print 'mm_per_pt:',mm_per_pt
    
    print 'G0 X0 Y0 Z%.3f' %(z_safe_height)
    
    #
    # generate nc point from bmp point mapping
    #
    last_x_pt = 0
    last_y_pt = 0
    
    for y in xrange(bmp.height):
        for x in xrange(bmp.width):
            (r,b,g) = bmp.bitmap[bmp.height-1-y][x]
            if r < 128:
                d = distance_p2p(x,y,last_x_pt,last_y_pt,mm_per_pt)
                #print 'd:',d
                if d >= jump_distance:
                    s  = 'G1 X%.3f Y%.3f Z%.3f\n' % (last_x_pt*mm_per_pt,last_y_pt*mm_per_pt,z_safe_height)
                    s +=  'G1 X%.3f Y%.3f Z%.3f\n' % (x*mm_per_pt,y*mm_per_pt,z_safe_height)
                    s +=  'G1 X%.3f Y%.3f Z%.3f' % (x*mm_per_pt,y*mm_per_pt,z_drill_height)
                    print s

                else:    
                    s = 'G1 X%.3f Y%.3f Z%.3f' % (x*mm_per_pt,y*mm_per_pt,z_drill_height)
                    print s
              
              
                last_x_pt = x
                last_y_pt = y
                
    bmp.save_to('new.bmp')




        