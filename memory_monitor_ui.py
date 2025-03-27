"""
@Author Name    : Saket Zanwar
@Date           : 26-March-2025
@Description    : This Python 2.7 script creates a simple Tkinter-based GUI to monitor the memory usage of the AutomationDesk.exe process.
It retrieves memory data using WMI, displays real-time logs in the interface, and lets users set a memory threshold and email recipients.
When memory usage exceeds the set threshold (or if the process crashes), the script automatically sends an alert email via Outlook.
Additionally, the GUI features a logo and version number, and all monitoring runs in a background thread with proper COM initialization.

"""
# -*- coding: utf-8 -*-

import Tkinter as tk          # Import Tkinter module for GUI (Python 2.7)
import threading              # For running the monitoring in a background thread
import time                   # For time-related functions
import logging                # For logging events and errors
import pythoncom              # For COM initialization in threads (required for WMI and Outlook)

# Import the memory monitoring function from memory_monitor.py
from memory_monitor import memory_monitor
# Import the Outlook alert function from alert_system.py
from alert_system import send_outlook_alert
# Import PIL modules for handling images (logo)
from PIL import Image, ImageTk

# Configure logging for the UI; log file 'memory_monitor_ui.log'
logging.basicConfig(filename="memory_monitor_ui.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class MemoryMonitorApp(object):
    def __init__(self, master):
        """Initialize the UI and default variables."""
        self.master = master
        self.master.title("Crash Monitoring Tool")  # Set window title
        self.master.geometry("720x600")
        self.master.configure(bg="#f4f4f4")

        # --- Load and Display Logo ---
        # This block attempts to load 'logo.png' from the same directory,
        # resize it, and display it in the top-left corner.
        try:
            logo_img = Image.open("logo.png")  # Open logo image
            # Resize image to 50x50; using ANTIALIAS (for Python 2.7 / older Pillow versions)
            logo_img = logo_img.resize((50, 50), Image.ANTIALIAS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)  # Convert to PhotoImage for Tkinter

            # Create a label to hold the logo and place it at coordinates (15, 10)
            self.logo_label = tk.Label(master, image=self.logo_tk, bg="white")
            self.logo_label.place(x=15, y=10)
        except Exception as e:
            logging.warning("Logo not loaded: %s", str(e))

        # --- Title Label ---
        # Displays the main title of the application in a bold font.
        self.header_label = tk.Label(master, text="Crash Monitoring Tool", font=("Arial", 16, "bold"), bg="#f4f4f4")
        self.header_label.pack(pady=10)

        # --- Version Label (Top Right) ---
        # Displays the version number in the top right corner.
        self.version_label = tk.Label(master, text="Version 1.0", font=("Arial", 10, "italic"), fg="gray", bg="#f4f4f4")
        self.version_label.place(x=625, y=10)

        # --- Email Recipients Input ---
        # Label and entry widget for user to input email addresses (semicolon-separated)
        self.email_label = tk.Label(master, text="Email Recipients (For multiple emails use semi-colon):", bg="#f4f4f4")
        self.email_label.pack(pady=5)
        self.email_entry = tk.Entry(master, width=60)
        self.email_entry.pack()

        # --- Alert Threshold Input ---
        # Label and entry widget for user to set the alert threshold percentage.
        self.threshold_label = tk.Label(master, text="Alert Threshold (%):", bg="#f4f4f4")
        self.threshold_label.pack(pady=5)
        self.threshold_entry = tk.Entry(master, width=10)
        self.threshold_entry.insert(0, "70")  # Default threshold value is 70%
        self.threshold_entry.pack()

        # --- Save Settings Button ---
        # Button to save the user settings (emails and threshold).
        self.save_button = tk.Button(master, text="Save Settings", command=self.save_settings, width=20, bg="lightblue")
        self.save_button.pack(pady=5)

        # --- Start & Stop Monitoring Buttons ---
        # Buttons to start and stop the memory monitoring process.
        self.start_button = tk.Button(master, text="Start Monitoring", command=self.start_monitoring, width=20)
        self.start_button.pack(pady=5)
        self.start_button.place(x=70, y=155)  # Fine placement for better layout

        self.stop_button = tk.Button(master, text="Stop Monitoring", command=self.stop_monitoring, width=20)
        self.stop_button.pack(pady=5)
        self.stop_button.place(x=500, y=155)  # Positioned on right side

        # --- Log Text Widget ---
        # Text widget to display real-time logs (memory usage, alerts, etc.).
        self.log_text = tk.Text(master, height=15, width=80)
        self.log_text.pack(pady=10)

        # --- Initialize Flags and Default Settings ---
        self.monitoring = False            # Flag to indicate if monitoring is active
        self.monitor_thread = None         # Thread object for monitoring
        self.emails = []                   # List of email addresses
        self.threshold = 70.0              # Alert threshold percentage
        self.last_alert_memory = None      # Track last alert memory percentage for 5% increments

    def save_settings(self):
        """Reads email recipients and threshold from the UI and saves them."""
        email_str = self.email_entry.get().strip()
        threshold_str = self.threshold_entry.get().strip()
        try:
            self.threshold = float(threshold_str)  # Convert threshold to float
        except ValueError:
            self.threshold = 70.0  # Default if conversion fails
        if email_str:
            # Split the email string by semicolon and remove extra whitespace
            self.emails = [e.strip() for e in email_str.split(";") if e.strip()]
        else:
            self.emails = []
        self.log_message("Settings saved: Emails = {} | Threshold = {}%".format(", ".join(self.emails), self.threshold))

    def start_monitoring(self):
        """Starts the memory monitoring in a background thread."""
        if not self.monitoring:
            self.monitoring = True
            self.last_alert_memory = None  # Reset the last alert value
            self.log_message("Started Monitoring AutomationDesk...")
            self.monitor_thread = threading.Thread(target=self.run_monitoring)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stops the memory monitoring process."""
        if self.monitoring:
            self.monitoring = False
            self.log_message("Stopped Monitoring AutomationDesk.")

    def run_monitoring(self):
        """
        Continuously calls memory_monitor() in a loop, checking usage and sending alerts.
        If AutomationDesk.exe is not found, a crash alert email is sent.
        """
        pythoncom.CoInitialize()  # Initialize COM for this thread
        try:
            while self.monitoring:
                # Call memory_monitor() to get current memory usage details
                found, vm_mb, ws_mb, memory_percentage = memory_monitor()

                if found:
                    # Log the memory usage details
                    msg = "Memory: {:.2f} MB ({:.2f}%) | Working Set: {:.2f} MB".format(vm_mb, memory_percentage, ws_mb)
                    self.log_message(msg)

                    # Check if memory usage exceeds the threshold
                    if memory_percentage >= self.threshold:
                        # Ensure alerts are only sent every 5% increment
                        if self.last_alert_memory is None or memory_percentage >= self.last_alert_memory + 5:
                            if self.emails:
                                send_outlook_alert("AutomationDesk.exe", vm_mb, ws_mb, memory_percentage, self.emails)
                                self.last_alert_memory = memory_percentage
                            else:
                                self.log_message("No recipients provided; skipping email alert.")
                else:
                    # Process not found (Crash detected)
                    self.log_message("Process not found: AutomationDesk.exe")
                    if self.emails:
                        send_outlook_alert("AutomationDesk.exe (CRASHED)", 0, 0, 0, self.emails, crash_detected=True)
                    else:
                        self.log_message("No recipients provided; skipping crash alert.")

                time.sleep(5)  # Wait for 5 seconds before next check
        finally:
            pythoncom.CoUninitialize()  # Uninitialize COM for this thread

    def log_message(self, msg):
        """Appends a timestamped log message to the UI log text widget."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.log_text.insert(tk.END, "[{}] {}\n".format(timestamp, msg))
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryMonitorApp(root)
    root.mainloop()
