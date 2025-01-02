import paramiko
import json
import re

def parse_ngrok_ssh(ssh_string):
    """Parses an ngrok SSH string into components."""
    pattern = r"ssh (.*?)@(.*?) -p (\d+)"
    match = re.match(pattern, ssh_string)
    if not match:
        raise ValueError("Invalid SSH string format.")
    return match.group(1), match.group(2), int(match.group(3))

def fetch_compute_specs(ssh_string, password):
    """Fetches system specifications from a remote machine via SSH."""
    username, hostname, port = parse_ngrok_ssh(ssh_string)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=hostname, port=port, username=username, password=password)

        # Fetch CPU specifications
        stdin, stdout, stderr = client.exec_command("lscpu")
        lscpu_output = stdout.read().decode()

        cpu_specs = {}
        for line in lscpu_output.splitlines():
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()

            if key == "CPU op-mode(s)":
                cpu_specs["op_modes"] = value
            elif key == "Address sizes":
                cpu_specs["address_sizes"] = value
            elif key == "Byte Order":
                cpu_specs["byte_order"] = value
            elif key == "CPU(s)":
                cpu_specs["total_cpus"] = int(value)
            elif key == "On-line CPU(s) list":
                cpu_specs["online_cpus"] = value
            elif key == "Vendor ID":
                cpu_specs["vendor_id"] = value
            elif key == "Model name":
                cpu_specs["cpu_name"] = value
            elif key == "CPU family":
                cpu_specs["cpu_family"] = int(value)
            elif key == "Model":
                cpu_specs["model"] = int(value)
            elif key == "Thread(s) per core":
                cpu_specs["threads_per_core"] = int(value)
            elif key == "Core(s) per socket":
                cpu_specs["cores_per_socket"] = int(value)
            elif key == "Socket(s)":
                cpu_specs["sockets"] = int(value)
            elif key == "CPU max MHz":
                cpu_specs["cpu_max_mhz"] = float(value)
            elif key == "CPU min MHz":
                cpu_specs["cpu_min_mhz"] = float(value)

        # Check for GPU (NVIDIA)
        gpu_info = {}
        stdin, stdout, stderr = client.exec_command("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
        nvidia_output = stdout.read().decode().strip()
        if nvidia_output:
            gpu_info = []
            for line in nvidia_output.splitlines():
                name, memory = line.split(',')
                gpu_info.append({
                    "gpu_name": name.strip(),
                    "memory_total": memory.strip()
                })

        # Fetch RAM information
        stdin, stdout, stderr = client.exec_command("free -h | grep Mem")
        ram_output = stdout.read().decode().strip()
        ram = ram_output.split()[1]  # Total memory

        # Fetch storage information
        stdin, stdout, stderr = client.exec_command("lsblk -o NAME,TYPE,SIZE,MOUNTPOINT | grep disk")
        storage_output = stdout.read().decode().strip()
        storage_lines = storage_output.splitlines()
        storage_info = []
        for line in storage_lines:
            parts = line.split()
            if len(parts) >= 3:
                storage_info.append({
                    "name": parts[0],
                    "type": "SSD" if "sd" in parts[0] else "HDD",
                    "capacity": parts[2]
                })

        # Fetch location dynamically (mocked as not directly available via SSH)
        location = "Unknown Location"  # Default placeholder

        # Construct the response
        compute_resource = {
            "resource_type": "GPU" if gpu_info else "CPU",
            "ram": ram,
            "storage": storage_info[0] if storage_info else {},
            "is_active": True,
            "cpu_specs": cpu_specs,
            "gpu_specs": gpu_info if gpu_info else None
        }

        return compute_resource

    except Exception as e:
        # Return inactive status if connection fails
        return {
            "resource_type": "Unknown",
            "ram": "Unknown",
            "storage": {},
            "is_active": False,
            "cpu_specs": {},
            "gpu_specs": None,
            "error": "Miner currently inactive. Error: " + str(e)
        }

    finally:
        client.close()



def compare_compute_resources(new_resource, existing_resource):
    """Compare new compute resource specs with existing ones and calculate a score."""
    score = 0
    total_checks = 0

    # Compare CPU specs
    for key in ["op_modes", "address_sizes", "byte_order", "total_cpus", "online_cpus", "vendor_id", "cpu_name", "cpu_family", "model", "threads_per_core", "cores_per_socket", "sockets", "cpu_max_mhz", "cpu_min_mhz"]:
        total_checks += 1
        new_value = new_resource["cpu_specs"].get(key)
        existing_value = existing_resource["cpu_specs"].get(key)
        
        # Handle numeric comparisons safely
        try:
            if isinstance(new_value, str) and isinstance(existing_value, str):
                if new_value == existing_value:
                    score += 1
            elif new_value is not None and existing_value is not None:
                if float(new_value) == float(existing_value):
                    score += 1
        except ValueError:
            # Skip comparison if conversion to float/int fails
            pass


    # Compare RAM
    total_checks += 1
    if new_resource.get("ram") == existing_resource.get("ram"):
        score += 1

    # Compare storage
    total_checks += 1
    if new_resource.get("storage", {}).get("capacity") == existing_resource.get("storage", {}).get("capacity"):
        score += 1

    # Compare resource type (CPU/GPU)
    total_checks += 1
    if new_resource.get("resource_type") == existing_resource.get("resource_type"):
        score += 1

    # Final score
    comparison_result = {
        "score": score,
        "total_checks": total_checks,
        "percentage": (score / total_checks) * 100
    }

    return comparison_result


def compute_resource_score(resource):
    """
    Calculate a score for a compute resource (CPU or GPU) based on its specifications.

    Parameters:
    resource (dict): A dictionary containing compute resource details.

    Returns:
    float: A score representing the performance of the resource.
    """
    score = 0
    weights = {
        "cpu": {
            "cores": 0.4,
            "threads_per_core": 0.1,
            "max_clock_speed": 0.3,
            "ram": 0.15,
            "storage_speed": 0.05
        },
        "gpu": {
            "vram": 0.5,
            "compute_cores": 0.3,
            "bandwidth": 0.2
        }
    }

    if resource["resource_type"] == "CPU":
        cpu_specs = resource.get("cpu_specs", {})
        ram = float(resource.get("ram", "0GB").replace("GB", ""))
        storage_speed = float(resource["storage"].get("read_speed", "0MB/s").replace("MB/s", ""))

        # Normalize CPU values for scoring
        cores_score = cpu_specs.get("total_cpus", 0) / 64  # Assuming max 64 cores
        threads_score = cpu_specs.get("threads_per_core", 0) / 2  # Assuming max 2 threads/core
        clock_speed_score = cpu_specs.get("cpu_max_mhz", 0) / 5000  # Assuming max 5 GHz
        ram_score = ram / 128  # Assuming max 128GB RAM
        storage_score = storage_speed / 1000  # Assuming max 1000MB/s

        # Weighted score for CPU
        score += (cores_score * weights["cpu"]["cores"] +
                  threads_score * weights["cpu"]["threads_per_core"] +
                  clock_speed_score * weights["cpu"]["max_clock_speed"] +
                  ram_score * weights["cpu"]["ram"] +
                  storage_score * weights["cpu"]["storage_speed"])

    elif resource["resource_type"] == "GPU":
        gpu_specs = resource.get("gpu_specs", {})
        vram = float(gpu_specs.get("vram", "0GB").replace("GB", ""))
        compute_cores = gpu_specs.get("compute_cores", 0)
        bandwidth = float(gpu_specs.get("bandwidth", "0GB/s").replace("GB/s", ""))

        # Normalize GPU values for scoring
        vram_score = vram / 48  # Assuming max 48GB VRAM
        compute_cores_score = compute_cores / 10000  # Assuming max 10k cores
        bandwidth_score = bandwidth / 1000  # Assuming max 1 TB/s

        # Weighted score for GPU
        score += (vram_score * weights["gpu"]["vram"] +
                  compute_cores_score * weights["gpu"]["compute_cores"] +
                  bandwidth_score * weights["gpu"]["bandwidth"])

    return round(score, 3)
