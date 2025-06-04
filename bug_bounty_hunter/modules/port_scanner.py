import socket
import sys

def scan_ports(target_host):
    """
    Scans a target host for open common ports.

    Args:
        target_host (str): The IP address or hostname to scan.

    Returns:
        list: A list of integers representing open ports.
    """
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
        3306, 3389, 5900, 8000, 8080, 8443
    ]
    open_ports = []

    print(f"[*] Scanning {target_host} for open ports...")

    try:
        # Resolve hostname to IP address first.
        # This also serves as a check if the host is resolvable.
        target_ip = socket.gethostbyname(target_host)
        print(f"[*] Target IP: {target_ip}")
    except socket.gaierror:
        print(f"[!] Hostname {target_host} could not be resolved. Exiting.")
        return []
    except Exception as e:
        print(f"[!] An error occurred resolving hostname {target_host}: {e}")
        return []

    for port in common_ports:
        sock = None  # Initialize sock to None
        try:
            # Create a new socket for each port attempt
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Set a timeout for the connection attempt (1 second)

            result = sock.connect_ex((target_ip, port)) # connect_ex returns error indicator

            if result == 0:
                print(f"[+] Port {port} is open")
                open_ports.append(port)
            # else:
                # Optionally, print closed ports for verbosity, but usually not desired.
                # print(f"[-] Port {port} is closed or filtered")

        except socket.error as e:
            # This might catch errors if the IP is valid but host is down/unreachable at socket creation
            print(f"[!] Socket error while connecting to {target_ip}:{port} - {e}")
        except Exception as e:
            # Catch any other unexpected errors for a specific port
            print(f"[!] An unexpected error occurred with port {port}: {e}")
        finally:
            if sock:
                sock.close()

    return open_ports

if __name__ == '__main__':
    # Example usage:
    # Using a public, generally available host for demonstration.
    # Replace with a host/IP you have permission to scan.
    # Scanning "scanme.nmap.org" which is explicitly for testing scanners.
    host_to_scan = "scanme.nmap.org"
    # Or use an IP directly: host_to_scan = "45.33.32.156" (IP for scanme.nmap.org at time of writing)

    print(f"[*] Starting port scan on {host_to_scan}")

    found_open_ports = scan_ports(host_to_scan)

    if found_open_ports:
        print("\n[*] Summary of open ports:")
        for port_num in found_open_ports:
            print(f"Port {port_num} is open")
    else:
        print(f"\n[*] No common ports found open on {host_to_scan}, or host was unreachable.")
