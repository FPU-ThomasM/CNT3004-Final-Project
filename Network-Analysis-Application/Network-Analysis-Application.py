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
    self.start_time_value = None
    self.end_time_value = None
    self.file_size = None
    self.stats = {}
    
  #this is a little easter egg, hi y'all!

  #Need a start time and a stop time function (replace record)
  #calculate transmission rate when stop time is called
  #stop time - start time = total time
  #time will take in from computer's current time 
  
  def start_time():
    self.start_time_value = time.perf_counter()

    if file_path is not None and os.path.exists(file_path):
      self.file_size = os.path.getsize(file_path)
    return self.start_time_value

  def stop_time(): #this replaces save stats, for both server and client
    self.end_time_value = time.perf_counter()

    if self.start_time_value is None:
      raise ValueError("start_time() must be called before stop_time().")

    total_time = self.end_time_value - self.start_time_value

    transmission_rate = self.file_size / total_time

    self.stats = {
      "role": self.role,
      "ip_address": self.address,
      "file_size_bytes": self.file_size,
      "total_time_seconds": round(total_time, 4),
      "transmission_rate_bps": round(transmission_rate, 2) if transmission_rate else None,
      "transmission_rate_mbps": round((transmission_rate / (1024 * 1024)), 4) if transmission_rate else None
    }

    return self.stats

  def save_stats(self, filename="analysis_results.json")
    results_path = Path("results")
    results_path.mkdir(exist_ok=True)

    json_path = results_path / filename

    with open(json_path, "w") as f:
      json.dump(self.stats, f, indent=4)

    return json_path




