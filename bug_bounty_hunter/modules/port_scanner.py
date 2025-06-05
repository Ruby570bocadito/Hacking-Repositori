import socket
import sys

def scan_ports(target_host, provided_ports=None):
    """
    Scans a target host for open common ports.

    Args:
        target_host (str): The IP address or hostname to scan.

    Returns:
        list: A list of integers representing open ports.
    """
    default_common_ports = [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
        3306, 3389, 5900, 8000, 8080, 8443
    ]

    ports_to_scan_list = []
    if provided_ports is None:
        ports_to_scan_list = default_common_ports
    else:
        ports_to_scan_list = provided_ports

    results = []
    target_ip = None

    # Informational print, acceptable before returning structured data
    print(f"[*] Scanning {target_host} for open ports...")

    try:
        target_ip = socket.gethostbyname(target_host)
        print(f"[*] Target IP: {target_ip}")
    except socket.gaierror:
        print(f"[!] Hostname {target_host} could not be resolved. Exiting port scan.")
        # Return early with information about the resolution failure
        return [{'port': None, 'status': 'host_not_resolved', 'service': None, 'error_message': f"Hostname {target_host} could not be resolved."}]
    except Exception as e:
        print(f"[!] An error occurred resolving hostname {target_host}: {e}. Exiting port scan.")
        return [{'port': None, 'status': 'host_resolution_error', 'service': None, 'error_message': str(e)}]

    for port in ports_to_scan_list: # Iterate over the correct list
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result_code = sock.connect_ex((target_ip, port))

            service_name = "unknown"
            try:
                service_name = socket.getservbyport(port)
            except OSError:
                pass # Keep service_name as "unknown" if not found

            if result_code == 0:
                results.append({'port': port, 'status': 'open', 'service': service_name})
            # Optionally, include closed ports in results if desired for JSON output
            # else:
            #     results.append({'port': port, 'status': 'closed', 'service': service_name})

        except socket.error as e:
            results.append({'port': port, 'status': 'error', 'service': 'unknown', 'error_message': f"Socket error: {e}"})
        except Exception as e:
            results.append({'port': port, 'status': 'error', 'service': 'unknown', 'error_message': f"Unexpected error: {e}"})
        finally:
            if sock:
                sock.close()

    return results

def print_results(results, target_host):
    """Prints port scan results in a human-readable format."""
    print(f"\n--- Port Scan Results for {target_host} ---")

    if not results:
        print("  No ports were scanned or an unexpected error occurred before scanning.")
        return

    # Check for host resolution errors first
    if results[0].get('status') == 'host_not_resolved' or results[0].get('status') == 'host_resolution_error':
        print(f"  [!] Error: {results[0]['error_message']}")
        return

    open_ports_found = False
    for res in results:
        if res['status'] == 'open':
            print(f"  [+] Port {res['port']} is open (Service: {res.get('service', 'unknown')})")
            open_ports_found = True
        # Optionally print errors for specific ports if they are included in results
        # elif res['status'] == 'error':
        #     print(f"  [!] Error scanning port {res['port']}: {res.get('error_message', 'Unknown error')}")

    if not open_ports_found:
        print(f"  No common ports found open on {target_host} from the list scanned.")

if __name__ == '__main__':
    host_to_scan_example = "scanme.nmap.org"

    print(f"[*] Example Port Scan for: {host_to_scan_example}")
    scan_results = scan_ports(host_to_scan_example)
    print_results(scan_results, host_to_scan_example)
