import math
import os
import numpy as np

def getminmax(vals):
 # get min and max of a list of lists or a list of numpy arrays
 #print(vals[0])
 mymin = np.amin(vals[0])
 mymax = np.amax(vals[0])
 for ii in range(1,len(vals)):
  mymin = min(mymin, np.amin(vals[ii]))
  mymax = max(mymax, np.amax(vals[ii]))
 return [mymin,mymax]


def getfreq(val,mm,flim=[440,880]):
 # takes "val", usually between mm[0] and mm[1], and maps it to the range flim[0] to flim[1].
 # But, does not throw an error if val is outside the range specified by mm.
 tmp = (val - mm[0])/(mm[1]-mm[0])
 return ( tmp*(flim[1]-flim[0]) + flim[0] )


# The R sonify syntax:
# sonify(x = NULL, y = NULL, waveform = c("sine", "square", "triangle", "sawtooth"), interpolation = c("spline", "linear", "constant"), duration = 5, flim = c(440, 880), ticks = NULL, tick_len = 0.05, pulse_len = 0, pulse_amp = 0.2, noise_interval = c(0, 0), noise_amp = 0.5, amp_level = 1, na_freq = 300, stereo = TRUE, smp_rate = 44100, play = TRUE, player = NULL, player_args = NULL)
# We'll copy that as closely as we can, as we implement features.

def sonify_sox(ylists,duration=5,interpolation="constant",flim=[440,880],filename="test.wav",sepdur=0.3):
 # ylists should be a list of lists, or a list of numpy arrays.
 # duration is the duration in seconds per trace.
 # the overall file will be slightly longer than length*number_of_traces
 # sepdur is the duration (in seconds) of the separator/counter tones between traces.
 # I tried sepdur=0.1 as a default and it seemed too short.

 # first, get the min and max of all the yvalues across all traces,
 # to help set the scaling to frequencies.
 mm = getminmax(ylists)
 
 commandstr="sox --combine concatenate"
 for ii in range(len(ylists)):
   tmpy = ylists[ii] 
   # for each trace of y values,
   # make a separator (if sepdur isn't 0) consisting of short beeps at flim[0] and flim[1] to establish the low and high ranges,
   # repeated as many times as the trace number (once for the first trace, twice for the 2nd trace).
   # At some point it would be good to switch to a base-10 system for that, or Morse Code or something, in case it's more traces than can easily be counted quickly.
   if ( sepdur > 0 ):
    for jj in range(ii+1):
     d= str(round(sepdur*0.2 , 2 ) )
     commandstr+=" \"|sox -n -p synth " + str(sepdur) + " sin " + str(flim[0]) + " fade " + d +" 0 "+ d +" \""
     commandstr+=" \"|sox -n -p synth " + str(sepdur) + " sin " + str(flim[1]) + " fade " + d +" 0 "+ d +" \""

   # Now generate the audio for this trace itself.
   # First, get the duration for each datapoint:
   wl=round(duration/len(tmpy) , 2) # rounding to keep command line short. 2 decimal digits (hundredths of a second) is probably all the resolution our ears need.
   # Though you could convince me that all datapoints should have the same duration,
   # set by the length of the longest of the traces.
   
   # Now loop through the y values:
   for jj in range(len(tmpy)):
    fp=round( getfreq(tmpy[jj],mm,flim) , 2 ) 
    #rounding to keep command line short. 2 decimal digits (hundredths of a hertz) is probably all the resolution our ears need.
    if ( interpolation=="constant" ):
     d= str(round( wl*0.2 , 2))
     commandstr+=" \"|sox -n -p synth " + str(wl) + " sin " + str(fp) + " fade " + d +" 0 "+ d +" \""
    else:
     if( jj+1 < len(tmpy) ): # if interpolating, we'll need to access the next component of tmpy. Check that we won't run off the end!
      lp=round( getfreq(tmpy[jj+1],mm,flim) , 2 )
      #rounding to keep command line short. 2 decimal digits (hundredths of a hertz) is probably all the resolution our ears need.
      # no fading if doing interpolation
      commandstr+=" \"|sox -n -p synth " + str(wl) + " sin " + str(fp) + ":" + str(lp)  + " \""
     
 commandstr += " " + filename
 print(commandstr)
 os.system(commandstr)
 # end of sonify_sox function

x1 = np.arange(0,6,0.3)
y1 = np.sin(x1)
y2 = 0.3*np.cos(x1)
sonify_sox( [y1,y2], duration=3,interpolation="constant",flim=[440,880],filename="test1_y1y2.wav",sepdur=0.3)
sonify_sox( [y1,y2], duration=3,interpolation="linear",flim=[440,880],filename="test2_y1y2.wav",sepdur=0.3)
#sonify(normalize(dataset))
#sonify(normalize(dataset2))
#sonify(normalize(dataset))

