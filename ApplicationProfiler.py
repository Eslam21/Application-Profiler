import os
import matplotlib.pyplot as plt
import numpy
import psutil
import subprocess

class Profiler:
    def __init__(self, pid, duration):
        self.pid = pid
        self.p = psutil.Process(pid)
        self.duration = duration

    def get_execution_path(self):
        try:
            # Get execution path of the process
            execution_path = self.p.exe()
            
            print(f"Execution path is: {execution_path}") 
        except psutil.NoSuchProcess:
            print(f"Process with PID {self.pid} does not exist.")
    
    def get_connections(self):
        # Process open connections
        open_connections = self.p.connections()
        print("Open Connections:")
        for conn in open_connections:
            print(f"  {conn.laddr} -> {conn.raddr}")
    
    def get_usage(self,bars=50):
        while True:
            cpu_usage=self.p.cpu_percent()
            mem_usage=self.p.memory_percent()
            cpu_percent = (cpu_usage/100.0)
            mem_percent=(mem_usage/100.0)
            cpu_bar='█'*int(cpu_percent*bars)+'-'*(bars-int(cpu_percent*bars))
            mem_bar='█'*int(mem_percent*bars)+'-'*(bars-int(mem_percent*bars))
            print(f"\rCPU Usage: |{cpu_bar}| {cpu_usage:.2f}% ",end="")
            print(f"  Mem Usage: |{mem_bar}| {mem_usage:.2f}% ",end="\r")
            
            time.sleep(self.duration)

    def get_threads(self):
        threads= self.p.threads()
        num_threads = len(threads)
        thread_ids = [thread for thread in range(num_threads)]
        user_times = [thread.user_time for thread in threads]
        system_times = [thread.system_time for thread in threads]

        # Stacked Bar Chart
        plt.figure(figsize=(10, 6))
        plt.bar(thread_ids, user_times, label='User Time', color='skyblue')
        plt.bar(thread_ids, system_times, bottom=user_times, label='System Time', color='orange')
        plt.xlabel('Thread ID')
        plt.ylabel('Time (seconds)')
        plt.title(f'Number of active threads is {num_threads} threads')
        plt.legend()
        plt.grid(True)
        # Set automatic tick positions and labels
        plt.xticks(thread_ids)
        # Adjust layout automatically
        plt.tight_layout()
        plt.show()

    def get_priority(self):
        # Process priority value
        priority = self.p.nice()
        print(f"Process Priority: {priority}")

    def get_status(self):
        # Process status
        status = self.p.status()
        print(f"Process Status: {status}")
        
    def get_process_info(self):
        """Function to get process information"""
        parent_process = self.p.parent()
        children_processes = self.p.children(recursive=True)
        
        # Print information
        print("Process:")
        print("  PID:", self.p.pid)
        print("  Name:", self.p.name())
        print("  Status:", self.p.status())

        if parent_process:
            print("Parent Process:")
            print("  PID:", parent_process.pid)
            print("  Name:", parent_process.name())
        else:
            print("Parent Process: None")

        print("Children Processes:")
        for child in children_processes:
            print("  PID:", child.pid)
            print("  Name:", child.name())



if __name__ == '__main__':
    # # Function to create a child process
    # def create_child_process():
    #     subprocess.Popen(["notepad.exe"])

    # # Start a child process
    # create_child_process()

    # # Get PID of the current process (the Python script)
    # current_pid = os.getpid()





    try:
        exe_path = input("Enter exe path:").replace('\\', '\\\\')
        print("path:", exe_path)
        process = subprocess.Popen(exe_path)
        pid=process.pid
        Profiler(pid, 1).get_execution_path()

    except Exception as e:
        print(e)