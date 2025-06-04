# Bug Bounty Hunter Tool

A simple command-line tool to assist in bug bounty reconnaissance by automating common tasks like subdomain enumeration, port scanning, directory bruteforcing, and Wayback Machine URL discovery.

## Features

*   **Subdomain Scanning:** Enumerates subdomains using a customizable wordlist.
*   **Port Scanning:** Scans for common open TCP ports on a target.
*   **Directory/File Bruteforcing:** Discovers accessible directories and files on a web server using a customizable wordlist.
*   **Wayback Machine URL Fetching:** Retrieves historical URLs for a domain from the Wayback Machine.

## Project Structure

*   `src/`: Contains the main executable script (`bug_bounty_tool.py`).
*   `modules/`: Houses the individual scanning modules (e.g., `subdomain_scanner.py`, `port_scanner.py`).
*   `wordlists/`: Stores default wordlists used by the scanning modules (e.g., `common_subdomains.txt`, `common_directories.txt`).
*   `reports/`: Intended for saving scan reports - functionality to be added in future updates.

## Prerequisites

*   Python 3.7+ (developed and tested with Python 3.10)
*   The `requests` library. Install with:
    ```bash
    pip install requests
    ```

## Setup / Installation

1.  **Clone the Repository:**
    ```bash
    # If using git
    # git clone <repository_url>
    # cd bug_bounty_hunter
    ```
    Alternatively, download and extract the project files into a `bug_bounty_hunter` directory.

2.  **Install Required Python Packages:**
    Navigate to the project's root directory (`bug_bounty_hunter`) and run:
    ```bash
    pip install requests
    ```

3.  **(Optional) Make the Main Script Executable:**
    This allows you to run the script directly without prefixing `python3`.
    ```bash
    chmod +x src/bug_bounty_tool.py
    ```
    If you do this, you can run the tool like `./src/bug_bounty_tool.py ...`

## Usage

All commands should be run from the root of the `bug_bounty_hunter` project directory.

The main script is `src/bug_bounty_tool.py`.

**Target Argument:**
*   For subdomain, port, and wayback scans, the `target` can be a domain name (e.g., `example.com`) or an IP address (for port scan).
*   For the directory/file bruteforce (`dir`) scan, the `target` should be a full URL (e.g., `http://example.com` or `https://example.com`). The script will attempt to prepend `http://` if a scheme is missing.

**Running Specific Scans:**

```bash
python3 src/bug_bounty_tool.py <target> --scans <scan_type_1> [<scan_type_2> ...]
```

*   **Subdomain Scan:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans subdomain
    ```
*   **Port Scan:**
    ```bash
    python3 src/bug_bounty_tool.py scanme.nmap.org --scans port
    ```
*   **Directory/File Bruteforce:**
    ```bash
    python3 src/bug_bounty_tool.py http://example.com --scans dir
    ```
*   **Wayback URLs:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans wayback
    ```
*   **Multiple Specific Scans:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans subdomain port
    ```

**Running All Scans:**

```bash
python3 src/bug_bounty_tool.py <target> --scans all
```
*Example:*
```bash
python3 src/bug_bounty_tool.py http://scanme.nmap.org --scans all
```

**Using Custom Wordlists:**

*   **Custom Subdomain Wordlist:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans subdomain --subdomain_wordlist path/to/your/subdomains.txt
    ```
*   **Custom Directory/File Wordlist:**
    ```bash
    python3 src/bug_bounty_tool.py http://example.com --scans dir --dir_wordlist path/to/your/directories.txt
    ```
    If custom wordlists are not provided, the tool defaults to using `wordlists/common_subdomains.txt` and `wordlists/common_directories.txt` respectively.

## Disclaimer

This tool is intended for educational purposes and for use in authorized security testing scenarios only. Always obtain explicit permission from the target system's owner before conducting any scanning or testing activities. Unauthorized scanning of systems is illegal and unethical. The developers of this tool are not responsible for any misuse or damage caused by this tool. Use responsibly.
