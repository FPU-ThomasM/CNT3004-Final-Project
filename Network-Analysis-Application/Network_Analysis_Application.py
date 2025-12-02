import os
import socket
import threading
from pathlib import Path
import json
import hashlib #these imports are based off the other modules
import time

SIZE = 65536 ## byte .. buffer size

class Analysis:
  def __init__(self, role, address): #initialization
    self.role = role
    self.address = address
    self.start_time_value = None
    self.end_time_value = None
    self.file_size = None
    self.stats = {}

  
  def start_time(self, file_path=None):
    self.start_time_value = time.perf_counter()

    #if file_path is not None and os.path.exists(file_path):
    #  self.file_size = os.path.getsize(file_path)
    return self.start_time_value

  def stop_time(self, file_path=None):
    self.end_time_value = time.perf_counter()

    if file_path is not None and os.path.exists(file_path):
      self.file_size = os.path.getsize(file_path)

    if self.start_time_value is None:
      raise ValueError("start_time() must be called before stop_time().")

    total_time = self.end_time_value - self.start_time_value

    transmission_rate = self.file_size / total_time

    self.stats = { #this is a python dictionary
      "role": self.role,
      "ip_address": self.address,
      "file_size_bytes": self.file_size,
      "total_time_seconds": round(total_time, 4),
      "transmission_rate_bps": round(transmission_rate, 2) if transmission_rate else None,
      "transmission_rate_mbps": round((transmission_rate / (SIZE * SIZE)), 4) if transmission_rate else None
    }
    
    return self.stats


  #this module saves the stats to computer running it
  def save_stats(self, filename="analysis_results.json"):
    results_path = Path("results")
    results_path.mkdir(exist_ok=True)

    json_path = results_path / filename

    with open(json_path, "w") as f:
      json.dump(self.stats, f, indent=4)

    return json_path










