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
  def record_stats():
    return 0 #placeholder code for me a place to start
  
  def save_stats():
    return 0 #placeholder 2
