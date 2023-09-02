import psutil
import json

usage_data = {}

# Disk usage
drive_letters = psutil.disk_partitions()
disk_data = {}

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
        # print(f"disk_usage for {drive_letter}: {disk_usage}")
    except Exception as ex:
        print(f"Error: {ex}")
        continue

usage_data['disk'] = disk_data

# RAM usage
ram_usage = psutil.virtual_memory()
ram_data = {
    'total': ram_usage.total,
    'available': ram_usage.available,
    'used': ram_usage.used,
    'free': ram_usage.free,
    'percent': ram_usage.percent
}
# print(f"RAM usage: {ram_data}")

usage_data['ram'] = ram_data

# CPU usage
cpu_percent = psutil.cpu_percent()
cpu_data = {
    'total': cpu_percent
}
# print(f"Total CPU usage: {cpu_data}")

usage_data['cpu'] = cpu_data

# Convert the data to JSON string
usage_data_json = json.dumps(usage_data)

# Write the JSON string to a file
with open("E:\\EricMon\\usage_data.json", "w") as json_file:
    json_file.write(usage_data_json)
