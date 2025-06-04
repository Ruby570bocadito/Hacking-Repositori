# network_scanner/local_scanner.py
import ipaddress
import subprocess
import platform # For OS detection
import socket # Added for port scanning

def get_network_range():
    """Prompts the user to enter the network range."""
    network_range = input("Enter the network range to scan (e.g., 192.168.1.0/24 or a single IP like 192.168.1.1): ")
    return network_range

def discover_devices(network_range_str):
    """Discovers active devices in the given network range using ping."""
    active_devices = []
    print(f"[*] Discovering devices in {network_range_str}...")

    try:
        network = ipaddress.ip_network(network_range_str, strict=False)
        ips_to_scan = list(network.hosts())
        if not ips_to_scan and network.num_addresses == 1: # Handle single IP entry like 192.168.1.1
             ips_to_scan = [network.network_address]
    except ValueError:
        print(f"[!] Invalid network range format: {network_range_str}. Please use CIDR (e.g., 192.168.1.0/24) or a single IP.")
        return active_devices

    if not ips_to_scan:
        print(f"[*] No valid IP addresses to scan in the provided range: {network_range_str}")
        return active_devices

    print(f"[*] Identified {len(ips_to_scan)} IP(s) to check in {network_range_str}.")

    for ip in ips_to_scan:
        ip_str = str(ip)
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
            timeout_value = '1000' if platform.system().lower() == 'windows' else '1'

            command = ['ping', param, '1', timeout_param, timeout_value, ip_str]
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)

            if process.returncode == 0:
                print(f"[+] Host {ip_str} is active.")
                active_devices.append(ip_str)
        except subprocess.TimeoutExpired:
            print(f"[-] Ping to {ip_str} timed out (subprocess).")
        except Exception as e:
            print(f"[!] Error pinging {ip_str}: {e}")
            continue
    return active_devices

def scan_ports(target_host):
    """
    Scans a target host for open common ports.
    Args:
        target_host (str): The IP address to scan.
    Returns:
        list: A list of integers representing open ports.
    """
    # More comprehensive list, including some from the original scanner and others.
    common_ports = [
        20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 137,
        138, 139, 143, 161, 162, 179, 389, 443, 445, 465, 500, 514, 515,
        548, 587, 631, 636, 873, 990, 993, 995, 1080, 1194, 1433, 1434,
        1521, 1701, 1723, 1812, 1813, 2000, 2049, 2222, 2375, 2376, 3000,
        3268, 3269, 3306, 3389, 5000, 5060, 5061, 5222, 5432, 5555, 5672,
        5900, 5901, 5902, 6000, 6379, 6667, 7000, 8000, 8008, 8080, 8443,
        8888, 9000, 9090, 9200, 9300, 9418, 10000, 11211, 27017, 27018,
        28017, 30000, 50070
    ]
    open_ports_found = []

    print(f"[*] Scanning {target_host} for open ports...")

    target_ip = target_host

    for port in common_ports:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5) # Reduced timeout for faster local scanning

            result = sock.connect_ex((target_ip, port))

            if result == 0:
                print(f"  [+] Port {port} on {target_ip} is open")
                open_ports_found.append(port)
        except socket.error as e:
            # This might occur if host becomes unreachable between ping and scan
            print(f"  [!] Socket error while connecting to {target_ip}:{port} - {e}")
            break # If host is down, no point trying other ports
        except Exception as e:
            print(f"  [!] An unexpected error occurred with port {port} on {target_ip}: {e}")
        finally:
            if sock:
                sock.close()

    if not open_ports_found:
        print(f"[*] No common ports found open on {target_ip}.")
    return open_ports_found

if __name__ == '__main__':
    target_range_str = get_network_range()
    all_open_ports_map = {} # To store {ip: [open_ports]}

    if target_range_str:
        print(f"[*] Network range to be scanned: {target_range_str}")
        active_hosts = discover_devices(target_range_str)

        if active_hosts:
            print("\n[*] Starting port scan on active devices...")
            for host_ip in active_hosts:
                open_ports = scan_ports(host_ip) # scan_ports now prints details
                if open_ports:
                    all_open_ports_map[host_ip] = open_ports

            print("\n[*] Scan Complete. Summary of open ports:")
            if all_open_ports_map:
                for ip, ports in all_open_ports_map.items():
                    print(f"  Host: {ip}")
                    for port_num in ports: # Renamed 'port' to 'port_num' to avoid conflict if __main__ was a function
                        print(f"    - Port {port_num} is open")
            else:
                print("  No open ports found on any active devices.")
        else:
            print("[*] No active devices found to scan.")
    else:
        print("[*] No network range provided.")
