# logo2grbl
A command line tool to translate LOGO instruction to GRBL serial command

Usage:<br>
<pre><code>
python logo2grbl.py CLI serial_port up_height down_height arc_min_len
python logo2grbl.py BATCH script_file serial_port up_height down_height arc_min_len

Examples:
python logo2grbl.py CLI COM3 5 -3 1
python logo2grbl.py BATCH logo.txt COM3 5 -3 1

</code></pre>

Anytime, you can press enter to show current x,y,z and heading information.<br>
You can view generated gcode.txt with http://jherrm.com/gcode-viewer/


logo sample file
<pre><code>
home
penup
# cut out inner circle
parc 360 4 0.3

# cut out 8 rect
rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

rt 45
fd 10
prect 1.25 6 0.3 0.3
prect -1.25 6 0.3 0.3
fd -10

# cut out outer circle finally
arc 360 16
</code></pre>
