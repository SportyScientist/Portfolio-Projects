import csv
import os
import psutil
import subprocess
import time

# Open the CSV file
with open('resource_usage.csv', 'w', newline='') as csvfile:
    fieldnames = ['timestamp', 'cpu', 'memory']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

# Run the script
script_path = '01_score_calculator.py'
process = subprocess.Popen(['python3', script_path])

max_cpu = 0
max_memory = 0

# Monitor resource consumption
while process.poll() is None:
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.Process(process.pid).memory_info()

    # Update the maximum values
    max_cpu = max(max_cpu, cpu_percent)
    max_memory = max(max_memory, memory_info.rss)

# Wait for the script to complete
process.wait()

# Write the maximum values to the CSV file
with open('resource_usage.csv', 'a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writerow({'timestamp': time.time(), 'cpu': max_cpu, 'memory': max_memory})

# Print the exit code
print(f'Exit code: {process.returncode}')