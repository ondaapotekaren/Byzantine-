# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Byzantine-/demokit/tcp_time.repy

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
  Author: Zachary Boka
    tcp_time.repy

  Start Date:
    3 May 2009
    Amended 5 July, 2009 to be an extension to time.repy

  Description:

    This module is an implementation of time_interface.repy

    Contacts a server running time_server.repy to get the current time from an
    NTP because only the server can communicate with an NTP.

    To use this module, make one call to time_updatetime() to get the
    time from the server.  This function also implicitly sets the time.  Then
    call time_gettime() every time the current time is needed.

"""

repyhelper.translate_and_import('time_interface.repy')

repyhelper.translate_and_import('advertise.repy')

repyhelper.translate_and_import('random.repy')

repyhelper.translate_and_import('sockettimeout.repy')



# This function contacts the server to get the time from a NTP
def tcp_time_updatetime(localport):
  """
  <Purpose>
    Opens a connection with a server hosting time_server.repy, which obtains the
    current time via a NTP, then calls time_settime(float(currenttime)) to set
    the current time to the received value form the server.

  <Arguments>
    localport:

      The local port which may be used in contacting NTP servers.  It is
      currently not used in this function, but must be present as an argument
      for compatibility issues with time.repy.

  <Exceptions>
    Exception raised if advertise_lookup("time_server") fails after
    ten tries.

    Exception raised when a connection is not able to be established with any of
    the servers running time_server.repy.

  <Side Effects>
    time_settime(float(currenttime)) is called to set the time.

  <Returns>
    Returns the server ip:port that it managed to successfully connect to

"""

  # Get the ips and ports of servers hosting time_server.repy, retrying nine
  # times if there is an exception.
  gotval = False
  attemptretrieval = 0
  while attemptretrieval < 2:
    try:
      serveraddresses = advertise_lookup("time_server")
    except Exception:
      attemptretrieval = attemptretrieval + 1
      sleep(2)                 # Look up the value again in 10 seconds
    else:
      if serveraddresses != [] and serveraddresses[0] != '':
        gotval = True	        # Successfully obtained the value
        break
      else:
        attemptretrieval = attemptretrieval + 1


  if not gotval:
    raise Exception("Unable to locate any servers running time_server.repy")


  timelength = 25  # Max length of string, representing the time, to be received
  shuffledserveraddresses = random_sample(serveraddresses,min(len(serveraddresses),5))

  # Open a connection with a random server hosting time_server.repy
  timeobtained = False
  serverindex = 0
  while serverindex < len(shuffledserveraddresses):
    remoteaddress = shuffledserveraddresses[serverindex].split(':')
    remoteip = remoteaddress[0]
    remoteport = int(remoteaddress[1])

    try:
      sockobject = timeout_openconn(remoteip,remoteport)
    except Exception:
      serverindex +=1
    else:
      timeobtained = True
      break


  if not timeobtained:
    raise Exception("Unable to open connection with any of the ",len(shuffledserveraddresses),"servers running time_server.repy.")


  currenttime =''
  while '$' not in currenttime:
    currenttime += sockobject.recv(20)
  sockobject.close()
  currenttime = float(currenttime[:-1])

  # finally, set the time
  time_settime(currenttime)

  return shuffledserveraddresses[serverindex]  




#register the update method
time_register_method('tcp',tcp_time_updatetime)

### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Byzantine-/demokit/tcp_time.repy
