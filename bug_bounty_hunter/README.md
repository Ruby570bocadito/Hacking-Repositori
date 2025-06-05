# Bug Bounty Hunter Tool

A simple command-line tool to assist in bug bounty reconnaissance by automating common tasks like subdomain enumeration, port scanning, directory bruteforcing, Wayback Machine URL discovery, HTTP header analysis, and robots.txt/sitemap parsing.

## Features

*   **Subdomain Scanning:** Enumerates subdomains using a customizable wordlist.
*   **Port Scanning:** Scans for common open TCP ports on a target.
*   **Directory/File Bruteforcing:** Discovers accessible directories and files on a web server using a customizable wordlist.
*   **Wayback Machine URL Fetching:** Retrieves historical URLs for a domain from the Wayback Machine.
*   **HTTP Header Analysis:** Fetches and analyzes HTTP headers, focusing on security-related headers.
*   **Robots.txt and Sitemap.xml Parsing:** Fetches and parses `robots.txt` and linked sitemaps to discover disallowed paths and listed URLs.

## Project Structure

*   `src/`: Contains the main executable script (`bug_bounty_tool.py`).
*   `modules/`: Houses the individual scanning modules (e.g., `subdomain_scanner.py`, `port_scanner.py`).
*   `wordlists/`: Stores default wordlists used by the scanning modules (e.g., `common_subdomains.txt`, `common_directories.txt`).
*   `reports/`: Default directory for saving JSON scan reports.

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

## Command-line Arguments

*   **`target`**: (Required) The primary target for the scans.
    *   For `subdomain`, `port`, and `wayback` scans: a domain name (e.g., `example.com`) or IP address (for port scan).
    *   For `dir` (directory bruteforce), `header` (HTTP headers), and `robots` (robots.txt/sitemap) scans: a base URL (e.g., `http://example.com` or `https://example.com`). The script will attempt to prepend `http://` if a scheme is missing for these scan types.

*   **`--scans <scan_type_1> [<scan_type_2> ...]`**: (Required) One or more scan types to perform.
    *   Choices: `subdomain`, `port`, `dir`, `wayback`, `header`, `robots`, `all`.
    *   `all` will run all available scan types.

*   **`--json_output <filepath>`**: (Optional) Save all scan results to the specified JSON file.
    *   If a filename without a path is given (e.g., `results.json`), it's saved in the `reports/` directory (which will be created if it doesn't exist).
    *   If a full path is given (e.g., `/path/to/results.json`), it's saved at that location.

*   **`--subdomain_wordlist <filepath>`**: (Optional) Path to a custom wordlist for subdomain scanning. Defaults to `wordlists/common_subdomains.txt`.

*   **`--dir_wordlist <filepath>`**: (Optional) Path to a custom wordlist for directory/file bruteforcing. Defaults to `wordlists/common_directories.txt`.

## Usage Examples

All commands should be run from the root of the `bug_bounty_hunter` project directory.

**Running Specific Scans:**

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
*   **HTTP Header Analysis:**
    ```bash
    python3 src/bug_bounty_tool.py https://example.com --scans header
    ```
*   **Robots.txt and Sitemap Analysis:**
    ```bash
    python3 src/bug_bounty_tool.py http://example.com --scans robots
    ```
*   **Multiple Specific Scans:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans subdomain port header
    ```

**Running All Scans:**

```bash
python3 src/bug_bounty_tool.py <target_url_or_domain> --scans all
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

**Saving Output to JSON:**

*   **Save all scan results for a target to a JSON file in the `reports/` directory:**
    ```bash
    python3 src/bug_bounty_tool.py https://example.com --scans all --json_output results.json
    ```
    *(This will create `reports/results.json`)*

*   **Save specific scan results to a JSON file with a specific path:**
    ```bash
    python3 src/bug_bounty_tool.py example.com --scans subdomain wayback --json_output /tmp/sub_wayback_results.json
    ```

## Disclaimer

This tool is intended for educational purposes and for use in authorized security testing scenarios only. Always obtain explicit permission from the target system's owner before conducting any scanning or testing activities. Unauthorized scanning of systems is illegal and unethical. The developers of this tool are not responsible for any misuse or damage caused by this tool. Use responsibly.
