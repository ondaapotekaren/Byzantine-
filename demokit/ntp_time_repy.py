# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Byzantine-/demokit/ntp_time.repy

### THIS FILE WILL BE OVERWRITTEN!
### DO NOT MAKE CHANGES HERE, INSTEAD EDIT THE ORIGINAL SOURCE FILE
###
### If changes to the src aren't propagating here, try manually deleting this file. 
### Deleting this file forces regeneration of a repy translation


from repyportability import *
import repyhelper
mycontext = repyhelper.get_shared_context()
callfunc = 'import'
callargs = []

"""
   Author: Justin Cappos
     Edited by Eric Kimbrel, this was originally time.repy 

   Start Date: 8 August 2008

   Description:

   This is an implementation of time_interface.repy

   This module handles getting the time from an external source, via UDP.
   It gets the remote time once and then uses the offset from the local 
   clock from then on
   to return the current time.

   To use this module, first make a call to time_updatetime(localport) with a
   local UDP port that you have permission to send/recv on. This will
   contact some random subset of NTP servers to get and store the local time.

   Then, to get the actual time, call time_gettime() which will return
   the current time (in seconds). time_gettime() can be called at any point
   after having called time_updatetime(localport) since time_gettime() simply
   calculates how much time has elapsed since the local time was originally 
   acquired from one of the NTP servers.

   Note that time_gettime() will raise TimeError if no NTP server responded or
   if time_updatetime(localport) was never previously called.  If time_gettime()
   fails, then time_updatetime(localport) can be called again to sample time
   from another random set of NTP servers.
"""


repyhelper.translate_and_import('time_interface.repy')

# Use for random sampling...
repyhelper.translate_and_import('random.repy')


timeservers = ["time-a.nist.gov", "time-b.nist.gov", 
    "time-a.timefreq.bldrdoc.gov", "time-b.timefreq.bldrdoc.gov", 
    "time-c.timefreq.bldrdoc.gov", "utcnist.colorado.edu", "time.nist.gov", 
    "nist.netservicesgroup.com"]




#BUG: Do I need to compensate for the time taken to contact the time server?    (#353)
def ntp_time_updatetime(localport):
  """
   <Purpose>
    Obtains and stores the local time from a subset of NTP servers.

   <Arguments>
    localport:
             The local port to be used when contacting the NTP server(s).

   <Exceptions>
    TimeError when getmyip() fails or one of the subset of NTP servers will not
    respond.

   <Side Effects>
    time_settime(currenttime) is called as the subprocess of a subprocess, which
    adjusts the current time.

   <Returns>
    None.
  """

  try:
    ip = getmyip()
  except Exception, e:
    raise TimeError, str(e)

  listenhandle = recvmess(ip,localport, _time_decode_NTP_packet)
  mycontext['ntp_time_got_time'] = False

  # I'm going to get the time from up to 5 sources and then use the median
  mycontext['ntp_time_received_times'] = []

  # always close the handle before returning...
  try: 
    # try five random servers times...
    for servername in random_sample(timeservers,5):

      # this sends a request, version 3 in "client mode"
      ntp_request_string = chr(27)+chr(0)*47
      try: 
        sendmess(servername,123, ntp_request_string, ip, localport) # 123 is the NTP port
      except Exception:
        # most likely a lookup error...
        continue

    # wait for 5 seconds for a response before retrying
    for junkiterations in range(10):
      sleep(.5)

      if mycontext['ntp_time_got_time']:
        # If we've had a response, we sleep one second, choose the time,
        # and then quit
        sleep(1)

        # set the time...
        _time_choose_NTP_time_to_settime()

        # clean-up and return
        stopcomm(listenhandle)
        return
    
    
  finally:
    stopcomm(listenhandle)

  # Failure, tried servers without luck...
  raise TimeError, "Time Server update failed.  Perhaps retry later..."



# We're choosing from a list of times to avoid problems like that in #879
def _time_choose_NTP_time_to_settime():
  timelist = mycontext['ntp_time_received_times'][:]

  # this may happen if there are concurrent calls to update the time.
  assert(len(timelist)>0)
  
  timelist.sort()
  
  # it's better to be slightly high than slightly low...  I'll set the time
  # to be the middle element or if there is a tie, I'll choose the bigger 
  # 'middle' element.   That means [1,2,3] would set 2, but [1,2,3,4] would
  # set 3.   I can get this by integer division by 2...

  time_settime(timelist[len(timelist) / 2])
  



### Do the conversion / decoding for NTP.   More details about the 
### format of NTP are at RFC 2030 (http://www.ietf.org/rfc/rfc2030.txt)

# this unpacks the data from the packet and changes it to a float
def _time_convert_timestamp_to_float(timestamp):
  integerpart = (ord(timestamp[0])<<24) + (ord(timestamp[1])<<16) + (ord(timestamp[2])<<8) + (ord(timestamp[3]))
  floatpart = (ord(timestamp[4])<<24) + (ord(timestamp[5])<<16) + (ord(timestamp[6])<<8) + (ord(timestamp[7]))
  return integerpart + floatpart / float(2**32)


def _time_decode_NTP_packet(ip, port, mess, ch):
  # I got a time response packet.   Remember it and notify that I got it.
  mycontext['ntp_time_received_times'].append(_time_convert_timestamp_to_float(mess[40:48]))
  mycontext['ntp_time_got_time'] = True


#register the update method
time_register_method('ntp',ntp_time_updatetime)

### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Byzantine-/demokit/ntp_time.repy
