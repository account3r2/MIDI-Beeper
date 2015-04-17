#MIDI Beeper  
  
MIDI beeper is a Python program to play MIDI ﬁles by beeping through the  
computer’s beeper instead of using proper sound circuits. If you try to play  
chords or polyphony, it will rapidly switch between alternate notes like an old  
ofﬁce telephone. It sounds awful, but it might be useful when you really have  
to play a MIDI ﬁle but have no sound device attached. It should work on any  
machine that has the “beep” command (install “beep” package from your Linux/Unix  
package manager). It has been tested on a PC speaker and on an NSLU2’s internal  
speaker.  
  
On the NSLU2, playing music with beep works in Debian etch but not so well in  
Debian Lenny; you can try compiling this modiﬁed beep.c instead (remember the  
chmod 4755 mentioned in the man page).  
  
At the time of writing, the original code for this project can be found at:  
http://people.ds.cam.ac.uk/ssb22/mwrhome/midi-beeper.html
