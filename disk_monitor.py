import json
import subprocess
import psutil
import shutil
import win32com.client
import socket
import time
from datetime import datetime

master = "241" # this is my master server, its name is 241
working_ip = socket.gethostbyname(socket.gethostname()).split(".")[3]
working_dir = "E:\\EricMon\\"
remote_working_dir = "\\\\2.2.2.xyz\\E$\\EricMon\\" # include your ip, xyz is any string, it will be updated by worker node

def get_usage(node):
    if node == master:
        # Get disk, RAM, and CPU usage for local server
        drive_letters = psutil.disk_partitions()
        disk_data = {}
        ram_data = {}
        cpu_data = {}

        for drive in drive_letters:
            drive_letter = drive.device

            try:
                disk_usage = psutil.disk_usage(drive_letter)
                disk_data[drive_letter] = {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent
                }
            except Exception as ex:
                print(f"Disk Usage Error for {drive_letter}: {ex}")
                continue

        try:
            ram_usage = psutil.virtual_memory()
            ram_data = {
                'total': ram_usage.total,
                'used': ram_usage.used,
                'free': ram_usage.available,
                'percent': ram_usage.percent
            }
        except Exception as ex:
            print(f"RAM Usage Error: {ex}")

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_data = {
                'total': cpu_percent
            }
        except Exception as ex:
            print(f"CPU Usage Error: {ex}")

        return disk_data, ram_data, cpu_data

    else:
        try:
            plink_command = [
                "plink", "-batch", "-pwfile", "C:\\location_dir_for_pass\\pass.txt", "-ssh",
                f"user@2.2.2.{node}", "python3",
                f"{remote_working_dir.replace('xyz', node)}remote_disk_monitor.py"
            ]
            process = subprocess.Popen(plink_command, shell=True)
            process.wait()
        except Exception as ex:
            print(f"Remote Server: {node}: error: {ex}")
        print(f"Remote Server: {node}: disk_monitoring executed successfully!")

        # Read disk_usage, ram_usage, and cpu_usage from JSON
        with open(remote_working_dir.replace('xyz', node) +
                  "\\usage_data.json", "r") as json_read:
            data_json = json_read.read()

        # Convert the JSON string to dictionaries
        data = json.loads(data_json)
        disk_data = data.get('disk', {})
        ram_data = data.get('ram', {})
        cpu_data = data.get('cpu', {})

        return disk_data, ram_data, cpu_data


if __name__ == "__main__":
    threshold = 90

    servers = ['241', '211', '221', '222', '242','231','232'] # add all your workder nodes including master which is 241 in my case
    html = "<html><body>"

    for node in servers:
        if node != master:
            copy_scripts = False
            while not copy_scripts:
                try:
                    shutil.copy(working_dir + "remote_disk_monitor.py",
                                remote_working_dir.replace("xyz",
                                                           node) +
                                "remote_disk_monitor.py")
                    print(f"Remote Server: {node} & {remote_working_dir.replace('xyz',node)}: disk_monitor.py copy Success")
                    copy_scripts = True
                except Exception as ex:
                    print(
                        f"Remote Server: {node} & {remote_working_dir.replace('xyz',node)}: remote_disk_monitor.py copy error: {ex}, Sleep for 30 seconds and try again!"
                    )
                    time.sleep(30)

        print(f"Node: {node}")
        disk_data, ram_data, cpu_data = get_usage(node)
        print(disk_data)
        print(ram_data)
        print(cpu_data)

        html += f"<h1>Usage for Server #{node}</h1>"
        html += "<h2>Disk Usage:</h2>"
        for drive, data in disk_data.items():
            drive_letter = drive.split(':')[0]
            usage_percentage = data['percent']
            used_size_gb = round(data['used'] / (1024**3), 2)
            total_size_gb = round(data['total'] / (1024**3), 2)
            color = "#26A0DA"  # Default color for normal usage

            if usage_percentage > 75:
                color = "#ffb74d"  # Orange for usage above 75%
            if usage_percentage > 90:
                color = "#e53935"  # Red for usage above 90%

            html += "<table style='width: 200px; border-collapse: collapse;'>"
            html += "<tr>"
            html += f"<td style='width: {usage_percentage}%; background-color: {color}; color: white;'><b>{drive_letter}:<b></td>"
            html += f"<td style='width: {100 - usage_percentage}%;background-color: #E6E6E6'></td>"
            html += "</tr>"
            html += f"<tr><td colspan='2' style='white-space: nowrap;'>{used_size_gb} GB / {total_size_gb} GB <b>({usage_percentage}% used)</b></td></tr>"
            html += "</table>"
            html += "<br>"

        html += "<h2>RAM Usage:</h2>"
        usage_percentage = ram_data.get('percent', 0)
        used_size_gb = round(ram_data.get('used', 0) / (1024**3), 2)
        total_size_gb = round(ram_data.get('total', 0) / (1024**3), 2)
        color = "#26A0DA"  # Default color for normal usage

        if usage_percentage > 75:
            color = "#ffb74d"  # Orange for usage above 75%
        if usage_percentage > 90:
            color = "#e53935"  # Red for usage above 90%

        html += "<table style='width: 200px; border-collapse: collapse;'>"
        html += "<tr>"
        html += f"<td style='width: {usage_percentage}%; background-color: {color}; color: white;'><b>RAM:<b></td>"
        html += f"<td style='width: {100 - usage_percentage}%;background-color: #E6E6E6'></td>"
        html += "</tr>"
        html += f"<tr><td colspan='2' style='white-space: nowrap;'>{used_size_gb} GB / {total_size_gb} GB <b>({usage_percentage}% used)</b></td></tr>"
        html += "</table>"
        html += "<br>"

        html += "<h2>CPU Usage:</h2>"
        usage_percentage = cpu_data.get('total', 0)
        color = "#26A0DA"  # Default color for normal usage

        if usage_percentage > 75:
            color = "#ffb74d"  # Orange for usage above 75%
        if usage_percentage > 90:
            color = "#e53935"  # Red for usage above 90%

        html += "<table style='width: 200px; border-collapse: collapse;'>"
        html += "<tr>"
        html += f"<td style='width: {usage_percentage}%; background-color: {color}; color: white;'><b>CPU:<b></td>"
        html += f"<td style='width: {100 - usage_percentage}%;background-color: #E6E6E6'></td>"
        html += "</tr>"
        html += f"<tr><td colspan='2' style='white-space: nowrap;'>{usage_percentage}% used</td></tr>"
        html += "</table>"
        html += "<br>"

    html += "</body></html>"

    outlook_obj = win32com.client.Dispatch(
        "Outlook.Application").CreateItem(0)
    outlook_obj.SentOnBehalfOfName = 'Outlook_email@outlook.com'
    # outlook_obj.To = "khaleel Ahmad <khaleel.org@gmail.com>;"
    outlook_obj.To = "all-your-email-recipients-list"
    outlook_obj.Subject = f"Disk, RAM, and CPU Usage | {datetime.now().strftime('%d-%m-%Y')}"
    outlook_obj.HTMLBody = html
    outlook_obj.Send()
