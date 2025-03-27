"""
@Author Name    : Saket Zanwar
@Date           : 26-March-2025
@Description    : This script sends HTML email alerts via Microsoft Outlook when a monitored process either exhibits high memory usage
or crashes. It formats the email with inline CSS for clear presentation, logs the alert details and errors to "alerts.log", and 
supports custom recipient lists.
"""
# -*- coding: utf-8 -*-

import win32com.client  # Import module to interact with COM objects (e.g., Outlook)
import logging          # Import logging module for alert logging

# Configure logging to write messages to "alerts.log" with INFO level and timestamps
logging.basicConfig(filename="alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")


def send_outlook_alert(process_name, vm_mb, ws_mb, memory_percentage, custom_recipients=None, crash_detected=False):
    """
    Sends an HTML email alert via Outlook.
    
    Parameters:
    - process_name: Name of the monitored process.
    - vm_mb: Virtual memory usage in MB.
    - ws_mb: Working set memory usage in MB.
    - memory_percentage: Memory usage percentage.
    - custom_recipients: List of recipient email addresses.
    - crash_detected: Boolean flag indicating if a crash alert should be sent.
    """
    # If no recipients are provided, log the info and exit the function.
    if not custom_recipients:
        logging.info("No email recipients provided. Skipping email alert.")
        return

    # Create a semicolon-separated string of email recipients.
    recipients_str = "; ".join(custom_recipients)

    try:
        # Initialize the Outlook application using COM.
        outlook = win32com.client.Dispatch("Outlook.Application")
        # Create a new email item.
        mail = outlook.CreateItem(0)
        # Set the email recipients.
        mail.To = recipients_str

        if crash_detected:
            # Set subject for a crash alert.
            mail.Subject = "[ALERT] Process Crash: {}".format(process_name)
            # Build the HTML body for a crash alert with inline CSS for styling.
            mail.HTMLBody = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                        .container {{ max-width: 600px; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: auto; }}
                        .header {{ background-color: #FF0000; color: white; text-align: center; padding: 10px; font-size: 20px; font-weight: bold; border-radius: 5px 5px 0 0; }}
                        .content {{ padding: 15px; font-size: 14px; }}
                        .footer {{ text-align: center; font-size: 12px; color: #777; padding-top: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">Process Crash Alert</div>
                        <div class="content">
                            <p>The process <strong>{}</strong> has crashed or stopped running unexpectedly.</p>
                            <p>Please investigate immediately.</p>
                        </div>
                        <div class="footer">
                            <p>Automated Monitoring System</p>
                        </div>
                    </div>
                </body>
                </html>
                """.format(process_name)
        else:
            # Set subject for a high memory usage alert.
            mail.Subject = "[ALERT] High Memory Usage Alert: {}".format(process_name)
            # Build the HTML body for a high memory usage alert with a table for metrics.
            mail.HTMLBody = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                        .container {{ max-width: 600px; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: auto; }}
                        .header {{ background-color: #D9534F; color: white; text-align: center; padding: 10px; font-size: 20px; font-weight: bold; border-radius: 5px 5px 0 0; }}
                        .content {{ padding: 15px; font-size: 14px; line-height: 1.6; }}
                        table {{ width: 100%%; border-collapse: collapse; margin-top: 10px; }}
                        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                        th {{ background-color: #f8f9fa; }}
                        .footer {{ text-align: center; font-size: 12px; color: #777; padding-top: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">High Memory Usage Alert</div>
                        <div class="content">
                            <p><strong>Process:</strong> {}</p>
                            <table>
                                <tr><th>Metric</th><th>Value</th></tr>
                                <tr><td>Virtual Memory</td><td><strong>{:.2f} MB ({:.2f}%%)</strong></td></tr>
                                <tr><td>Working Set</td><td>{:.2f} MB</td></tr>
                            </table>
                            <p>Please check the system immediately.</p>
                        </div>
                        <div class="footer">
                            <p>Automated Monitoring System</p>
                        </div>
                    </div>
                </body>
                </html>
                """.format(process_name, vm_mb, memory_percentage, ws_mb)

            # Send the email.
            mail.Send()
            # Log the alert details after sending the email.
            log_alert(process_name, vm_mb, ws_mb, memory_percentage, recipients_str, crash_detected)
    except Exception as e:
        # Log any errors encountered while trying to send the email.
        logging.error("Error sending email alert: %s", str(e))


def log_alert(process_name, vm_mb, ws_mb, memory_percentage, recipients_str, crash_detected):
    """
    Logs the alert details.
    
    Depending on whether a crash was detected, it formats the log message accordingly.
    """
    if crash_detected:
        message = "Crash Alert for {} - Recipients: {}".format(process_name, recipients_str)
    else:
        message = ("Alert Sent for {} - VM: {:.2f} MB ({:.2f}%%), WS: {:.2f} MB - Recipients: {}"
                   .format(process_name, vm_mb, memory_percentage, ws_mb, recipients_str))

    # Log the alert information.
    logging.info(message)
    # Also print the alert message to the console.
    print(message)

if __name__ == "__main__":
    # Test usage: Send a high memory usage alert with sample data.
    test_recipients = ["user1@example.com", "user2@example.com"]
    send_outlook_alert("AutomationDesk.exe", 2048.0, 256.0, 50.0, test_recipients)
    # Test usage: Send a crash alert for the process with sample data.
    send_outlook_alert("AutomationDesk.exe", 0, 0, 0, test_recipients, crash_detected=True)
