import os
import psutil
import graphviz
import pandas as pd
import subprocess
import time

class Profiler:
    """
    Profiler class to monitor and retrieve information about a specific process.
    
    Attributes:
        pid (int): Process ID of the target process.
        p (psutil.Process): psutil.Process instance for the target process.
        duration (int): Duration between successive data fetches.
    """

    def __init__(self, pid: int, duration: int) -> None:
        """
        Initialize the Profiler with a process ID and a duration.

        Args:
            pid (int): Process ID of the target process.
            duration (int): Duration between successive data fetches.
        """
        self.pid = pid
        self.p = psutil.Process(pid)
        self.duration = duration

    def get_execution_path(self) -> str:
        """
        Get the execution path of the target process.

        Returns:
            str: Execution path of the process.
        """
        try:
            return self.p.exe()
        except psutil.NoSuchProcess:
            print(f"Process with PID {self.pid} does not exist.")
            return ""

    def get_connections(self) -> None:
        """
        Print open connections of the target process.
        """
        open_connections = self.p.connections()
        print("Open Connections:")
        for conn in open_connections:
            print(f"  {conn.laddr} -> {conn.raddr}")

    def get_usage(self) -> tuple[float, float]:
        """
        Get the CPU and memory usage of the target process.

        Returns:
            tuple: CPU usage (float) and memory usage (float) of the process.
        """
        cpu_usage = self.p.cpu_percent()
        mem_usage = self.p.memory_percent()
        return cpu_usage, mem_usage

    def get_threads(self) -> tuple[int, list[int], list[float], list[float]]:
        """
        Get the thread statistics of the target process.

        Returns:
            tuple: Number of threads, list of thread IDs, list of user times, list of system times.
        """
        threads = self.p.threads()
        num_threads = len(threads)
        thread_ids = [thread.id for thread in threads]
        user_times = [thread.user_time for thread in threads]
        system_times = [thread.system_time for thread in threads]
        return num_threads, thread_ids, user_times, system_times

    def get_priority(self) -> str:
        """
        Get the scheduling priority of the target process.

        Returns:
            str: Scheduling priority of the process.
        """
        nice_value = self.p.nice()
        if psutil.WINDOWS:
            priority_map = {
                psutil.IDLE_PRIORITY_CLASS: "Idle",
                psutil.BELOW_NORMAL_PRIORITY_CLASS: "Below Normal",
                psutil.NORMAL_PRIORITY_CLASS: "Normal",
                psutil.ABOVE_NORMAL_PRIORITY_CLASS: "Above Normal",
                psutil.HIGH_PRIORITY_CLASS: "High",
                psutil.REALTIME_PRIORITY_CLASS: "Realtime"
            }
            return priority_map.get(nice_value, "Unknown")
        else:
            if nice_value < -10:
                return "High"
            elif nice_value < 0:
                return "Above Normal"
            elif nice_value == 0:
                return "Normal"
            elif nice_value < 10:
                return "Below Normal"
            else:
                return "Low"

    def get_status(self) -> str:
        """
        Get the current status of the target process.

        Returns:
            str: Status of the process.
        """
        return self.p.status()

    def get_process_info(self) -> pd.DataFrame:
        """
        Get detailed information about the target process, its parent, and its children.

        Returns:
            pd.DataFrame: DataFrame containing process information.
        """
        parent_process = self.p.parent()
        children_processes = self.p.children(recursive=True)
        
        data = [["Current Process", self.p.pid, self.p.name(), self.p.status()]]
        if parent_process:
            data.append(["Parent Process", parent_process.pid, parent_process.name(), "N/A"])
        
        for child in children_processes:
            data.append(["Child Process", child.pid, child.name(), "N/A"])
        
        return pd.DataFrame(data, columns=["Type", "PID", "Name", "Status"])

    def create_process_graph(self) -> graphviz.Digraph:
        """
        Create a Graphviz graph for the process and its relations.

        Returns:
            graphviz.Digraph: Graph showing the process relationships.
        """
        graph = graphviz.Digraph()

        graph.node(str(self.p.pid), f"Current Process\nPID: {self.p.pid}\nName: {self.p.name()}")
        
        parent_process = self.p.parent()
        if parent_process:
            graph.node(str(parent_process.pid), f"Parent Process\nPID: {parent_process.pid}\nName: {parent_process.name()}")
            graph.edge(str(parent_process.pid), str(self.p.pid))
        
        children_processes = self.p.children(recursive=True)
        for child in children_processes:
            graph.node(str(child.pid), f"Child Process\nPID: {child.pid}\nName: {child.name()}")
            graph.edge(str(self.p.pid), str(child.pid))
        
        return graph

    def io_counters(self) -> dict[str, int]:
        """
        Get I/O counters for the target process.

        Returns:
            dict: Dictionary containing I/O counters.
        """
        io_count = self.p.io_counters()
        return {
            'read_count': io_count.read_count,
            'write_count': io_count.write_count,
            'read_bytes': io_count.read_bytes,
            'write_bytes': io_count.write_bytes,
            'other_count': io_count.other_count,
            'other_bytes': io_count.other_bytes
        }

    def terminate(self) -> None:
        """
        Terminate the target process.
        """
        self.p.terminate()


if __name__ == '__main__':
    # try:
    #     exe_path = input("Enter exe path: ").replace('\\', '\\\\')
    #     print("path:", exe_path)
    #     process = subprocess.Popen(exe_path)
    #     pid = process.pid
    #     profiler = Profiler(pid, 1)
    #     execution_path = profiler.get_execution_path()
    #     print("Execution Path:", execution_path)
    # except Exception as e:
    #     print(e)
    pass
