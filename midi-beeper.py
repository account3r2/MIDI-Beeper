#!/usr/bin/env python

# MIDI beeper (plays MIDI without sound hardware)
# Version 1.3, (c) 2007-2010 Silas S. Brown.  License: GPL

# MIDI beeper is a Python program to play MIDI by beeping
# through the computer's beeper instead of using proper
# sound circuits.  It emulates chords/polyphony.
# It sounds awful, but it might be useful when no sound device
# is attached.  It should work on any machine that has the
# "beep" Linux package, including NSLU2 network storage devices.

force_monophonic = 0  # set this to 1 to have only the top line (not normally necessary)

# On NSLU2, before running this script, as root do
# modprobe isp4xx_beeper

# ----------------------------------------------------

import os

# NSLU2 hack:
try: event=open("/proc/bus/input/devices").read()
except IOError: event=""
if "ixp4xx beeper" in event:
    h=event[event.find("Handlers=",event.index("ixp4xx beeper")):]
    event="-e /dev/input/"+(h[:h.find("\n")].split()[-1])
    import os ; os.system("sync") # just in case (beep has been known to crash NSLU2 Debian Etch in rare conditions)
else: event=""

min_pulseLength, max_pulseLength = 10,20 # milliseconds
repetitions_to_aim_for = 1 # arpeggiating each chord only once will do if it's brief
def chord(freqList,millisecs):
    if not freqList: return " -D %d" % (millisecs,) # rest
    elif len(freqList)==1: return " -n -f %d -l %d" % (freqList[0],millisecs) # one note
    else:
        pulseLength = max(min(millisecs/len(freqList)/repetitions_to_aim_for,max_pulseLength),min_pulseLength)
        return (" -D 0".join([chord([f],pulseLength) for f in freqList]))*max(1,millisecs/pulseLength/len(freqList)) # (max with 1 means at least 1 repetition - prefer a slight slow-down to missing a chord out)
    # (the above -D 0 is necessary because Debian 5's beep adds a default delay otherwise)

command_line_len = 80000 # reduce this if you get "argument list too long" (NB the real limit is slightly more than this value)

def runBeep(params):
    while " -n" in params: # not entirely silence
        params=params[params.find(" -n")+3:] # discard the initial "-n" and any delay before it
        brkAt = params.find(" -n",command_line_len)
        if brkAt>-1: thisP,params = params[:brkAt],params[brkAt:]
        else: thisP,params = params,""
        os.system("beep "+event+" "+thisP)

A=440 # you can change this if you want to re-pitch
midi_note_to_freq = []
import math
for i in range(128): midi_note_to_freq.append((A/32.0)*math.pow(2,(len(midi_note_to_freq)-9)/12.0))
assert midi_note_to_freq[69] == A # (comment this out if using floating-point tuning because it might fail due to rounding)

cumulative_params = []
current_chord = [[],0]
def add_midi_note_chord(noteNos,microsecs):
    millisecs = microsecs / 1000
    global current_chord
    if force_monophonic and noteNos: noteNos=[max(noteNos)]
    else: noteNos.sort()
    if noteNos == current_chord[0]:
        # it's just an extention of the existing one
        current_chord[1] += millisecs
        return
    else:
        add_midi_note_chord_real(current_chord[0],current_chord[1])
        current_chord = [noteNos,millisecs]
def add_midi_note_chord_real(noteNos,millisecs):
    def to_freq(n):
        if n==int(n): return midi_note_to_freq[int(n)]
        else: return (A/32.0)*math.pow(2,(n-9)/12.0)
    if noteNos and cumulative_params and not "-D" in cumulative_params[-1].split()[-2:]: cumulative_params.append("-D 0") # necessary because Debian 5's beep adds a default delay otherwise
    cumulative_params.append(chord(map(lambda x:to_freq(x),noteNos),millisecs))

# Some of the code below is taken from Python Midi Package by Max M,
# http://www.mxm.dk/products/public/pythonmidi
# with much cutting-down and modifying
import sys
from types import StringType
from cStringIO import StringIO
from struct import pack, unpack
def getNibbles(byte): return (byte >> 4 & 0xF, byte & 0xF)
def setNibbles(hiNibble, loNibble):
    return (hiNibble << 4) + loNibble
def readBew(value):
    return unpack('>%s' % {1:'B', 2:'H', 4:'L'}[len(value)], value)[0]
def readVar(value):
    sum = 0
    for byte in unpack('%sB' % len(value), value):
        sum = (sum << 7) + (byte & 0x7F)
        if not 0x80 & byte: break 
    return sum
def varLen(value):
    if value <= 127:
        return 1
    elif value <= 16383:
        return 2
    elif value <= 2097151:
        return 3
    else:
        return 4
def to_n_bits(value, length=1, nbits=7):
    bytes = [(value >> (i*nbits)) & 0x7F for i in range(length)]
    bytes.reverse()
    return bytes
def toBytes(value):
    return unpack('%sB' % len(value), value)
def fromBytes(value):
    if not value:
        return ''
    return pack('%sB' % len(value), *value)
NOTE_OFF = 0x80
NOTE_ON = 0x90
AFTERTOUCH = 0xA0
CONTINUOUS_CONTROLLER = 0xB0 
PATCH_CHANGE = 0xC0
CHANNEL_PRESSURE = 0xD0
PITCH_BEND = 0xE0
BANK_SELECT = 0x00
MODULATION_WHEEL = 0x01
BREATH_CONTROLLER = 0x02
FOOT_CONTROLLER = 0x04
PORTAMENTO_TIME = 0x05
DATA_ENTRY = 0x06
CHANNEL_VOLUME = 0x07
BALANCE = 0x08
PAN = 0x0A
EXPRESSION_CONTROLLER = 0x0B
EFFECT_CONTROL_1 = 0x0C
EFFECT_CONTROL_2 = 0x0D
GEN_PURPOSE_CONTROLLER_1 = 0x10
GEN_PURPOSE_CONTROLLER_2 = 0x11
GEN_PURPOSE_CONTROLLER_3 = 0x12
GEN_PURPOSE_CONTROLLER_4 = 0x13
BANK_SELECT = 0x20
MODULATION_WHEEL = 0x21
BREATH_CONTROLLER = 0x22
FOOT_CONTROLLER = 0x24
PORTAMENTO_TIME = 0x25
DATA_ENTRY = 0x26
CHANNEL_VOLUME = 0x27
BALANCE = 0x28
PAN = 0x2A
EXPRESSION_CONTROLLER = 0x2B
EFFECT_CONTROL_1 = 0x2C
EFFECT_CONTROL_2 = 0x2D
GENERAL_PURPOSE_CONTROLLER_1 = 0x30
GENERAL_PURPOSE_CONTROLLER_2 = 0x31
GENERAL_PURPOSE_CONTROLLER_3 = 0x32
GENERAL_PURPOSE_CONTROLLER_4 = 0x33
SUSTAIN_ONOFF = 0x40
PORTAMENTO_ONOFF = 0x41
SOSTENUTO_ONOFF = 0x42
SOFT_PEDAL_ONOFF = 0x43
LEGATO_ONOFF = 0x44
HOLD_2_ONOFF = 0x45
SOUND_CONTROLLER_1 = 0x46                  
SOUND_CONTROLLER_2 = 0x47                  
SOUND_CONTROLLER_3 = 0x48                  
SOUND_CONTROLLER_4 = 0x49                  
SOUND_CONTROLLER_5 = 0x4A                  
SOUND_CONTROLLER_7 = 0x4C                  
SOUND_CONTROLLER_8 = 0x4D                  
SOUND_CONTROLLER_9 = 0x4E                  
SOUND_CONTROLLER_10 = 0x4F                 
GENERAL_PURPOSE_CONTROLLER_5 = 0x50
GENERAL_PURPOSE_CONTROLLER_6 = 0x51
GENERAL_PURPOSE_CONTROLLER_7 = 0x52
GENERAL_PURPOSE_CONTROLLER_8 = 0x53
PORTAMENTO_CONTROL = 0x54                  
EFFECTS_1 = 0x5B                           
EFFECTS_2 = 0x5C                           
EFFECTS_3 = 0x5D                           
EFFECTS_4 = 0x5E                           
EFFECTS_5 = 0x5F                           
DATA_INCREMENT = 0x60                      
DATA_DECREMENT = 0x61                      
NON_REGISTERED_PARAMETER_NUMBER = 0x62     
NON_REGISTERED_PARAMETER_NUMBER = 0x63     
REGISTERED_PARAMETER_NUMBER = 0x64         
REGISTERED_PARAMETER_NUMBER = 0x65         
ALL_SOUND_OFF = 0x78
RESET_ALL_CONTROLLERS = 0x79
LOCAL_CONTROL_ONOFF = 0x7A
ALL_NOTES_OFF = 0x7B
OMNI_MODE_OFF = 0x7C          
OMNI_MODE_ON = 0x7D           
MONO_MODE_ON = 0x7E           
POLY_MODE_ON = 0x7F           
SYSTEM_EXCLUSIVE = 0xF0
MTC = 0xF1 
SONG_POSITION_POINTER = 0xF2
SONG_SELECT = 0xF3
TUNING_REQUEST = 0xF6
END_OFF_EXCLUSIVE = 0xF7 
SEQUENCE_NUMBER = 0x00      
TEXT            = 0x01      
COPYRIGHT       = 0x02      
SEQUENCE_NAME   = 0x03      
INSTRUMENT_NAME = 0x04      
LYRIC           = 0x05      
MARKER          = 0x06      
CUEPOINT        = 0x07      
PROGRAM_NAME    = 0x08      
DEVICE_NAME     = 0x09      
MIDI_CH_PREFIX  = 0x20      
MIDI_PORT       = 0x21      
END_OF_TRACK    = 0x2F      
TEMPO           = 0x51      
SMTP_OFFSET     = 0x54      
TIME_SIGNATURE  = 0x58      
KEY_SIGNATURE   = 0x59      
SPECIFIC        = 0x7F      
FILE_HEADER     = 'MThd'
TRACK_HEADER    = 'MTrk'
TIMING_CLOCK   = 0xF8
SONG_START     = 0xFA
SONG_CONTINUE  = 0xFB
SONG_STOP      = 0xFC
ACTIVE_SENSING = 0xFE
SYSTEM_RESET   = 0xFF
META_EVENT     = 0xFF
def is_status(byte):
    return (byte & 0x80) == 0x80 
class MidiToBeep:
    def update_time(self, new_time=0, relative=1):
        if relative:
            self._relative_time = new_time
            self._absolute_time += new_time
        else:
            self._relative_time = new_time - self._absolute_time
            self._absolute_time = new_time
        if self._relative_time:
            # time was advanced, so output something
            d = {}
            for c,v in self.current_notes_on: d[v+self.semitonesAdd[c]]=1
            if self.need_to_interleave_tracks: self.tracks[-1].append([d.keys(),self._relative_time*self.microsecsPerDivision])
            else: add_midi_note_chord(d.keys(),self._relative_time*self.microsecsPerDivision)
    def reset_time(self):
        self._relative_time = 0
        self._absolute_time = 0
    def rel_time(self): return self._relative_time
    def abs_time(self): return self._absolute_time
    def reset_run_stat(self): self._running_status = None
    def set_run_stat(self, new_status): self._running_status = new_status
    def get_run_stat(self): return self._running_status
    def set_current_track(self, new_track): self._current_track = new_track
    def get_current_track(self): return self._current_track
    def __init__(self):
        self._absolute_time = 0
        self._relative_time = 0
        self._current_track = 0
        self._running_status = None
        self.current_notes_on = []
        self.rpnLsb = [0]*16
        self.rpnMsb = [0]*16
        self.semitoneRange = [1]*16
        self.semitonesAdd = [0]*16
        self.microsecsPerDivision = 10000
    def note_on(self, channel=0, note=0x40, velocity=0x40):
        if velocity and not channel==9: self.current_notes_on.append((channel,note))
    def note_off(self, channel=0, note=0x40, velocity=0x40):
        try: self.current_notes_on.remove((channel,note))
        except ValueError: pass
    def aftertouch(self, channel=0, note=0x40, velocity=0x40): pass
    def continuous_controller(self, channel, controller, value):
        # Interpret "pitch bend range":
        if controller==64: self.rpnLsb[channel] = value
        elif controller==65: self.rpnMsb[channel] = value
        elif controller==6 and self.rpnLsb[channel]==self.rpnMsb[channel]==0:
            self.semitoneRange[channel]=value
    def patch_change(self, channel, patch): pass
    def channel_pressure(self, channel, pressure): pass
    def pitch_bend(self, channel, value):
        # Pitch bend is sometimes used for slurs
        # so we'd better interpret it (only MSB for now; full range is over 8192)
        self.semitonesAdd[channel] = (value-64)*self.semitoneRange[channel]/64.0
    def sysex_event(self, data): pass
    def midi_time_code(self, msg_type, values): pass
    def song_position_pointer(self, value): pass
    def song_select(self, songNumber): pass
    def tuning_request(self): pass
    def header(self, format=0, nTracks=1, division=96):
        self.division=division
        self.need_to_interleave_tracks = (format==1)
        self.tracks = [[]][:]
    def eof(self):
        if self.need_to_interleave_tracks:
            while True: # delete empty tracks
                try: self.tracks.remove([])
                except ValueError: break
            while self.tracks:
                minLen = min([t[0][1] for t in self.tracks])
                d = {}
                for t in self.tracks: d.update([(n,1) for n in t[0][0]])
                add_midi_note_chord(d.keys(),minLen)
                for t in self.tracks:
                    t[0][1] -= minLen
                    if t[0][1]==0: del t[0]
                while True: # delete empty tracks
                    try: self.tracks.remove([])
                    except ValueError: break
    def meta_event(self, meta_type, data): pass
    def start_of_track(self, n_track=0):
        self.reset_time()
        self._current_track += 1
        if self.need_to_interleave_tracks: self.tracks.append([])
    def end_of_track(self): pass
    def sequence_number(self, value): pass
    def text(self, text): pass
    def copyright(self, text): pass
    def sequence_name(self, text): pass
    def instrument_name(self, text): pass
    def lyric(self, text): pass
    def marker(self, text): pass
    def cuepoint(self, text): pass
    def program_name(self,progname): pass
    def device_name(self,devicename): pass
    def midi_ch_prefix(self, channel): pass
    def midi_port(self, value): pass
    def tempo(self, value):
        # TODO if need_to_interleave_tracks, and tempo is not already put in on all tracks, and there's a tempo command that's not at the start and/or not on 1st track, we may need to do something
        self.microsecsPerDivision = value/self.division
    def smtp_offset(self, hour, minute, second, frame, framePart): pass
    def time_signature(self, nn, dd, cc, bb): pass
    def key_signature(self, sf, mi): pass
    def sequencer_specific(self, data): pass

class RawInstreamFile:
    def __init__(self, infile=''):
        if infile:
            if isinstance(infile, StringType):
                infile = open(infile, 'rb')
                self.data = infile.read()
                infile.close()
            else:
                self.data = infile.read()
        else:
            self.data = ''
        self.cursor = 0
    def setData(self, data=''):
        self.data = data
    def setCursor(self, position=0):
        self.cursor = position
    def getCursor(self):
        return self.cursor
    def moveCursor(self, relative_position=0):
        self.cursor += relative_position
    def nextSlice(self, length, move_cursor=1):
        c = self.cursor
        slc = self.data[c:c+length]
        if move_cursor:
            self.moveCursor(length)
        return slc
    def readBew(self, n_bytes=1, move_cursor=1):
        return readBew(self.nextSlice(n_bytes, move_cursor))
    def readVarLen(self):
        MAX_VARLEN = 4 
        var = readVar(self.nextSlice(MAX_VARLEN, 0))
        self.moveCursor(varLen(var))
        return var
class EventDispatcher:
    def __init__(self, outstream):
        self.outstream = outstream
        self.convert_zero_velocity = 1
        self.dispatch_continuos_controllers = 1 
        self.dispatch_meta_events = 1
    def header(self, format, nTracks, division):
        self.outstream.header(format, nTracks, division)
    def start_of_track(self, current_track):
        self.outstream.set_current_track(current_track)
        self.outstream.start_of_track(current_track)
    def sysex_event(self, data):
        self.outstream.sysex_event(data)
    def eof(self):
        self.outstream.eof()
    def update_time(self, new_time=0, relative=1):
        self.outstream.update_time(new_time, relative)
    def reset_time(self):
        self.outstream.reset_time()
    def channel_messages(self, hi_nible, channel, data):
        stream = self.outstream
        data = toBytes(data)
        if (NOTE_ON & 0xF0) == hi_nible:
            note, velocity = data
            if velocity==0 and self.convert_zero_velocity:
                stream.note_off(channel, note, 0x40)
            else:
                stream.note_on(channel, note, velocity)
        elif (NOTE_OFF & 0xF0) == hi_nible:
            note, velocity = data
            stream.note_off(channel, note, velocity)
        elif (AFTERTOUCH & 0xF0) == hi_nible:
            note, velocity = data
            stream.aftertouch(channel, note, velocity)
        elif (CONTINUOUS_CONTROLLER & 0xF0) == hi_nible:
            controller, value = data
            if self.dispatch_continuos_controllers:
                self.continuous_controllers(channel, controller, value)
            else:
                stream.continuous_controller(channel, controller, value)
        elif (PATCH_CHANGE & 0xF0) == hi_nible:
            program = data[0]
            stream.patch_change(channel, program)
        elif (CHANNEL_PRESSURE & 0xF0) == hi_nible:
            pressure = data[0]
            stream.channel_pressure(channel, pressure)
        elif (PITCH_BEND & 0xF0) == hi_nible:
            hibyte, lobyte = data
            value = (hibyte<<7) + lobyte
            stream.pitch_bend(channel, value)
        else:
            raise ValueError, 'Illegal channel message!'
    def continuous_controllers(self, channel, controller, value):
        stream = self.outstream
        stream.continuous_controller(channel, controller, value)
    def system_commons(self, common_type, common_data):
        stream = self.outstream
        if common_type == MTC:
            data = readBew(common_data)
            msg_type = (data & 0x07) >> 4
            values = (data & 0x0F)
            stream.midi_time_code(msg_type, values)
        elif common_type == SONG_POSITION_POINTER:
            hibyte, lobyte = toBytes(common_data)
            value = (hibyte<<7) + lobyte
            stream.song_position_pointer(value)
        elif common_type == SONG_SELECT:
            data = readBew(common_data)
            stream.song_select(data)
        elif common_type == TUNING_REQUEST:
            stream.tuning_request(time=None)
    def meta_events(self, meta_type, data):
        stream = self.outstream
        if meta_type == SEQUENCE_NUMBER:
            number = readBew(data)
            stream.sequence_number(number)
        elif meta_type == TEXT:
            stream.text(data)
        elif meta_type == COPYRIGHT:
            stream.copyright(data)
        elif meta_type == SEQUENCE_NAME:
            stream.sequence_name(data)
        elif meta_type == INSTRUMENT_NAME:
            stream.instrument_name(data)
        elif meta_type == LYRIC:
            stream.lyric(data)
        elif meta_type == MARKER:
            stream.marker(data)
        elif meta_type == CUEPOINT:
            stream.cuepoint(data)
        elif meta_type == PROGRAM_NAME:
            stream.program_name(data)
        elif meta_type == DEVICE_NAME:
            stream.device_name(data)
        elif meta_type == MIDI_CH_PREFIX:
            channel = readBew(data)
            stream.midi_ch_prefix(channel)
        elif meta_type == MIDI_PORT:
            port = readBew(data)
            stream.midi_port(port)
        elif meta_type == END_OF_TRACK:
            stream.end_of_track()
        elif meta_type == TEMPO:
            b1, b2, b3 = toBytes(data)
            stream.tempo((b1<<16) + (b2<<8) + b3)
        elif meta_type == SMTP_OFFSET:
            hour, minute, second, frame, framePart = toBytes(data)
            stream.smtp_offset(
                    hour, minute, second, frame, framePart)
        elif meta_type == TIME_SIGNATURE:
            nn, dd, cc, bb = toBytes(data)
            stream.time_signature(nn, dd, cc, bb)
        elif meta_type == KEY_SIGNATURE:
            sf, mi = toBytes(data)
            stream.key_signature(sf, mi)
        elif meta_type == SPECIFIC:
            meta_data = toBytes(data)
            stream.sequencer_specific(meta_data)
        else: 
            meta_data = toBytes(data)
            stream.meta_event(meta_type, meta_data)
class MidiFileParser:
    def __init__(self, raw_in, outstream):
        self.raw_in = raw_in
        self.dispatch = EventDispatcher(outstream)
        self._running_status = None
    def parseMThdChunk(self):
        raw_in = self.raw_in
        header_chunk_type = raw_in.nextSlice(4)
        header_chunk_zise = raw_in.readBew(4)
        if header_chunk_type != 'MThd': raise TypeError, "It is not a valid midi file!"
        self.format = raw_in.readBew(2)
        self.nTracks = raw_in.readBew(2)
        self.division = raw_in.readBew(2)
        if header_chunk_zise > 6:
            raw_in.moveCursor(header_chunk_zise-6)
        self.dispatch.header(self.format, self.nTracks, self.division)
    def parseMTrkChunk(self):
        self.dispatch.reset_time()
        dispatch = self.dispatch
        raw_in = self.raw_in
        dispatch.start_of_track(self._current_track)
        raw_in.moveCursor(4)
        tracklength = raw_in.readBew(4)
        track_endposition = raw_in.getCursor() + tracklength 
        while raw_in.getCursor() < track_endposition:
            time = raw_in.readVarLen()
            dispatch.update_time(time)
            peak_ahead = raw_in.readBew(move_cursor=0)
            if (peak_ahead & 0x80): 
                status = self._running_status = raw_in.readBew()
            else:
                status = self._running_status
            hi_nible, lo_nible = status & 0xF0, status & 0x0F
            if status == META_EVENT:
                meta_type = raw_in.readBew()
                meta_length = raw_in.readVarLen()
                meta_data = raw_in.nextSlice(meta_length)
                dispatch.meta_events(meta_type, meta_data)
            elif status == SYSTEM_EXCLUSIVE:
                sysex_length = raw_in.readVarLen()
                sysex_data = raw_in.nextSlice(sysex_length-1)
                if raw_in.readBew(move_cursor=0) == END_OFF_EXCLUSIVE:
                    eo_sysex = raw_in.readBew()
                dispatch.sysex_event(sysex_data)
            elif hi_nible == 0xF0: 
                data_sizes = {
                    MTC:1,
                    SONG_POSITION_POINTER:2,
                    SONG_SELECT:1,
                }
                data_size = data_sizes.get(hi_nible, 0)
                common_data = raw_in.nextSlice(data_size)
                common_type = lo_nible
                dispatch.system_common(common_type, common_data)
            else:
                data_sizes = {
                    PATCH_CHANGE:1,
                    CHANNEL_PRESSURE:1,
                    NOTE_OFF:2,
                    NOTE_ON:2,
                    AFTERTOUCH:2,
                    CONTINUOUS_CONTROLLER:2,
                    PITCH_BEND:2,
                }
                data_size = data_sizes.get(hi_nible, 0)
                channel_data = raw_in.nextSlice(data_size)
                event_type, channel = hi_nible, lo_nible
                dispatch.channel_messages(event_type, channel, channel_data)
    def parseMTrkChunks(self):
        for t in range(self.nTracks):
            self._current_track = t
            self.parseMTrkChunk() 
        self.dispatch.eof()
class MidiInFile:
    def __init__(self, outStream, infile=''):
        self.raw_in = RawInstreamFile(infile)
        self.parser = MidiFileParser(self.raw_in, outStream)
    def read(self):
        p = self.parser
        p.parseMThdChunk()
        p.parseMTrkChunks()
    def setData(self, data=''):
        self.raw_in.setData(data)

print "MIDI Beeper (c) 2007-2010 Silas S. Brown.  License: GPL"
if len(sys.argv)<2:
    print "Syntax: python midi-beeper.py MIDI-filename ..."
for midiFile in sys.argv[1:]:
    cumulative_params = []
    current_chord = [[],0][:]
    print "Parsing MIDI file",midiFile
    MidiInFile(MidiToBeep(), open(midiFile,"rb")).read()
    print "Playing",midiFile
    add_midi_note_chord([],0) # ensure flushed
    runBeep(" ".join(cumulative_params))
