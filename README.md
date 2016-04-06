# logo2grbl
A command line tool to translate LOGO instruction to GRBL serial command

Usage:<br>
<pre><code>
python logo2grbl.py serial_port up_height down_height arc_min_len
</code></pre>

Anytime, you can press enter to show current x,y,z and heading information.<br>
You can reivew generated gcode.txt with http://jherrm.com/gcode-viewer/

<pre><code>
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

</code></pre>

