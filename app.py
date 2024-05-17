import streamlit as st
import pandas as pd
import subprocess
import time
import psutil
from ApplicationProfiler import Profiler  

# Set page title and layout
st.set_page_config(page_title="Real-Time Application Profiling", layout="wide")
st.title("Real-Time Application Profiling")

# Get the path to the EXE application from user input
path = st.text_input("Enter Path of the EXE Application:", value="")
profile_button = st.button('Start Profiling')

if path and profile_button:
    try:
        # Display profiling message
        st.write(f"Profiling application at: {path}")
        
        # Launch the application
        exe_path = path.replace('\\', '\\\\')  # Adjust path for subprocess
        process = subprocess.Popen(exe_path)
        pid = process.pid
        prof = Profiler(pid, 1)  # Initialize profiler with process ID and interval

        # Initialize variables for metrics tracking
        prev_cpu_percent, prev_mem_percent = 0.0, 0.0
        io_read_counts, io_write_counts, io_read_bytes = [], [], []
        io_write_bytes, io_other_counts, io_other_bytes = [], [], []
        timestamps = []

        placeholder = st.empty()

        # Main loop for real-time metrics update
        while True:
            # Fetch system metrics using psutil
            cpu_freq = psutil.cpu_freq().current / 1000  # CPU frequency in GHz
            virtual_mem = psutil.virtual_memory()
            total_ram = virtual_mem.total / (1024 ** 3)  # Total RAM in GB
            used_ram = virtual_mem.used / (1024 ** 3)  # Used RAM in GB
            disk_usage = psutil.disk_usage('/')
            total_disk = disk_usage.total / (1024 ** 3)  # Total disk space in GB
            used_disk = disk_usage.used / (1024 ** 3)  # Used disk space in GB
            free_disk = disk_usage.free / (1024 ** 3)  # Free disk space in GB
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent / (1024 ** 2)  # Bytes sent in MB
            bytes_recv = net_io.bytes_recv / (1024 ** 2)  # Bytes received in MB

            # Fetch process-specific metrics using Profiler
            cpu_percent, mem_percent = prof.get_usage()
            cpu_delta, mem_delta = (cpu_percent - prev_cpu_percent), (mem_percent - prev_mem_percent)
            status, priority = prof.get_status(), prof.get_priority()

            # Fetch thread statistics
            num_threads, thread_ids, user_times, system_times = prof.get_threads()
            thread_data = pd.DataFrame({
                'Thread ID': thread_ids,
                'User Time': user_times,
                'System Time': system_times
            })

            # Fetch process information and relationships
            process_info = prof.get_process_info()
            process_graph = prof.create_process_graph()

            # Fetch I/O counters
            io_counters = prof.io_counters()

            # Append current values to lists
            io_read_counts.append(io_counters['read_count'])
            io_write_counts.append(io_counters['write_count'])
            io_read_bytes.append(io_counters['read_bytes'])
            io_write_bytes.append(io_counters['write_bytes'])
            io_other_counts.append(io_counters['other_count'])
            io_other_bytes.append(io_counters['other_bytes'])
            timestamps.append(time.strftime('%H:%M:%S'))

            # Update UI with metrics using Streamlit components
            with placeholder.container():
                # Display system metrics
                colA, colB, colC, colD = st.columns(4)
                colA.metric("CPU Frequency", f"{cpu_freq:.2f} GHz")
                colB.metric("RAM Usage", f"{used_ram:.2f} GB / {total_ram:.2f} GB")
                colC.metric("Bytes Sent/Received", f"{bytes_sent:.2f} / {bytes_recv:.2f} MB")
                colD.metric("Free Disk", f"{free_disk:.2f} GB")

                # Display process metrics
                col0, col1, col2, col3, col4 = st.columns(5)
                col0.metric("Status", status)
                col1.metric("Scheduling Priority", priority)
                col2.metric("Process ID", pid)
                col3.metric("Memory Usage", f"{mem_percent:.3f}%", f"{mem_delta:+.3f}%")
                col4.metric("CPU Usage", f"{cpu_percent:.3f}%", f"{cpu_delta:+.3f}%")

                # Display thread statistics
                st.title("Thread Statistics")
                st.bar_chart(thread_data.set_index('Thread ID'))

                # Display process information and relationships
                infoA, infoB = st.columns(2)
                infoA.header("Process Information")
                infoA.table(process_info)
                infoB.header("Process Relationships")
                infoB.graphviz_chart(process_graph)

                # Display I/O counts and bytes over time
                io_count_df = pd.DataFrame({
                    'IO Read Count': io_read_counts,
                    'IO Write Count': io_write_counts,
                    'IO Other Count': io_other_counts
                })
                io_bytes_df = pd.DataFrame({
                    'IO Read Bytes': io_read_bytes,
                    'IO Write Bytes': io_write_bytes,
                    'IO Other Bytes': io_other_bytes
                })

                chartA, chartB = st.columns(2)
                chartA.title("Process I/O Bytes")
                chartA.area_chart(io_bytes_df, use_container_width=True)
                chartB.title("Process I/O Count")
                chartB.line_chart(io_count_df)

            # Update previous values for delta calculations
            prev_cpu_percent = cpu_percent
            prev_mem_percent = mem_percent

            # Delay before fetching metrics again
            time.sleep(1)

    except Exception as e:
        st.warning(f"Error occurred: {e}")
        prof.terminate()  # Terminate profiling in case of error to clean up resources
