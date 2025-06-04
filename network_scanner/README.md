# Local Network Scanner

`local_scanner.py` is a Python script designed to discover active devices on your local network and scan them for common open TCP ports.

## Features

*   **Device Discovery:** Identifies active hosts on the specified network range using ICMP pings.
*   **Port Scanning:** Scans a predefined list of common TCP ports on each discovered active host.
*   **Cross-Platform (Ping):** Uses system `ping` commands compatible with Linux, macOS, and Windows for device discovery.
*   **User-Defined Network Range:** Prompts the user to specify the network range to scan (e.g., `192.168.1.0/24` or a single IP like `192.168.1.10`).

## Prerequisites

*   Python 3.x
*   The `ping` utility must be available in your system's PATH. This is standard on most operating systems.
*   Root/administrator privileges may be required for the `ping` command to function correctly on some systems, especially if firewalls are restrictive or for certain types of ICMP requests (though standard pings are usually allowed for users). The port scanning part itself (TCP connect scans) typically does not require root privileges.

## Usage

1.  **Navigate to the `network_scanner` directory:**
    ```bash
    cd path/to/your_repo/network_scanner
    ```

2.  **Run the script:**
    ```bash
    python3 local_scanner.py
    ```

3.  **Enter the network range when prompted:**
    For example:
    *   `192.168.1.0/24` (to scan all usable host IPs in the 192.168.1.x subnet)
    *   `10.0.0.5` (to scan only the single IP 10.0.0.5)

The script will then output the active devices found and any open common ports on those devices.

## How it Works

1.  **Network Range Input:** The script first asks you to provide a network range in CIDR notation (e.g., `192.168.1.0/24`) or as a single IP address.
2.  **IP Address Generation:** It generates a list of all possible host IP addresses within that range.
3.  **Device Discovery (Ping):** For each IP address, it sends an ICMP echo request (ping) using the system's `ping` command.
    *   If a response is received, the IP address is marked as an active device.
4.  **Port Scanning:** For each active device identified:
    *   It attempts to connect to a predefined list of common TCP ports.
    *   If a connection to a port is successful, that port is marked as open for that device.
5.  **Results Display:** The script prints live updates as devices are found and ports are scanned. A final summary of all discovered devices and their open ports is displayed at the end.

## Disclaimer

*   This tool is intended for educational purposes and for use on networks where you have explicit permission to scan.
*   Always ensure you have authorization before scanning any network or device. Unauthorized scanning can be disruptive and is often against terms of service or legal regulations.
*   The accuracy of device discovery can be affected by firewalls (on the target machine or network firewalls) that block ICMP echo requests. Similarly, port scan results can be affected by firewalls.
```
