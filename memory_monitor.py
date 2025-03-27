"""
@Author Name    : Saket Zanwar
@Date           : 26-March-2025
@Description    : This script monitors the memory usage of "AutomationDesk.exe" on Windows using WMI. It logs any errors, calculates the
process's virtual and working set memory in MB, computes its usage percentage based on a 4GB total memory assumption,
and prints the results.
"""
# -*- coding: utf-8 -*-
import wmi       # Import the wmi module to interact with Windows Management Instrumentation
import logging   # Import logging module to record log messages and errors

# Configure logging to output messages to 'memory_monitor.log'
logging.basicConfig(
    filename="memory_monitor.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(message)s"
)

def memory_monitor():
    """
    Checks the memory usage of AutomationDesk.exe once.
    
    Returns:
        tuple: (found, vm_mb, ws_mb, memory_percentage)
            - found (bool): True if the process is found, False otherwise.
            - vm_mb (float): Virtual memory usage in megabytes (MB).
            - ws_mb (float): Working set (physical memory usage) in MB.
            - memory_percentage (float): Percentage of total memory (assumed to be 4096 MB) used by the process.
    """
    # Create a WMI object for querying system information
    c = wmi.WMI()
    process_name = "AutomationDesk.exe"  # The target process name
    found = False       # Flag to indicate if the process was found
    vm_mb = 0.0         # Virtual memory in MB
    ws_mb = 0.0         # Working set memory in MB
    memory_percentage = 0.0  # Memory usage percentage relative to total memory

    try:
        # Loop through all running processes using WMI
        for process in c.Win32_Process():
            # Compare the process name in a case-insensitive manner
            if process.Name.lower() == process_name.lower():
                found = True  # Process found
                # Retrieve the virtual memory size in bytes; default to 0 if None
                vs_bytes = float(process.VirtualSize or 0)
                # Retrieve the working set size in bytes; default to 0 if None
                ws_bytes = float(process.WorkingSetSize or 0)
                # Convert the virtual and working set sizes from bytes to megabytes (MB)
                vm_mb = vs_bytes / (1024.0 * 1024.0)
                ws_mb = ws_bytes / (1024.0 * 1024.0)
                # Assume a total system memory of 4096 MB (4GB); adjust as necessary
                total_memory = 4096.0  
                # Calculate the memory usage percentage based on virtual memory usage
                memory_percentage = (vm_mb / total_memory) * 100.0
                # Once the process is found and measured, exit the loop
                break
    except Exception as e:
        # Log any errors encountered during the memory monitoring process
        logging.error("Error reading memory usage: %s", str(e))

    # Return a tuple with the results: (found flag, virtual memory in MB, working set in MB, memory usage percentage)
    return (found, vm_mb, ws_mb, memory_percentage)

if __name__ == "__main__":
    # Quick test: Run the memory monitor function if this script is executed directly
    found, vm_mb, ws_mb, mem_pct = memory_monitor()
    if found:
        # If the process is found, display its memory usage details
        print("Found AutomationDesk.exe. VM: {:.2f} MB, WS: {:.2f} MB, Usage: {:.2f}%".format(vm_mb, ws_mb, mem_pct))
    else:
        # Inform the user if the process is not running
        print("AutomationDesk.exe not found.")
