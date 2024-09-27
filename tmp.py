   # slurm_exporter.py
   from prometheus_client import start_http_server, Gauge
   import subprocess
   import time

   # Define a Prometheus gauge metric to track SLURM wait times
   slurm_wait_time = Gauge('slurm_wait_time_seconds', 'SLURM job wait time in seconds')

   def get_slurm_wait_times():
       # Run the SLURM command to get job wait times
       result = subprocess.run(['squeue', '--format=%M', '--state=PENDING'], stdout=subprocess.PIPE)
       wait_times = result.stdout.decode('utf-8').strip().split('\n')[1:]  # Skip header

       # Convert wait times to seconds and return the average
       total_wait_time = 0
       for wait_time in wait_times:
           h, m, s = map(int, wait_time.split(':'))
           total_wait_time += h * 3600 + m * 60 + s

       return total_wait_time / len(wait_times) if wait_times else 0

   if __name__ == '__main__':
       # Start up the server to expose the metrics.
       start_http_server(8000)
       while True:
           # Update the gauge with the current wait time
           slurm_wait_time.set(get_slurm_wait_times())
           time.sleep(60)  # Update every minute
