import os
import socket
import threading
from pathlib import Path
import json
import hashlib #these imports are based off the other modules

class Analysis:
  def __init__(self, role, address): #you need to define the class, figure out the role, and get the IP address for each part
    self.role = role
    self.address = address
    
  #this is a little easter egg, hi y'all!

  #Need a start time and a stop time function (replace record)
  #calculate transmission rate when stop time is called
  #stop time - start time = total time
  #time will take in from computer's current time 
  
  
  def record_stats():
    return 0 #placeholder code for me a place to start
  
  def save_stats():
    return 0 #placeholder 2
    #this function needs to be both for the server AND client

