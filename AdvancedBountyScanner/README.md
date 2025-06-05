# AdvancedBountyScanner

AdvancedBountyScanner is an active web application scanner designed to assist in bug bounty hunting and security testing. It automates the process of testing for common web vulnerabilities like SQL Injection (SQLi) and Cross-Site Scripting (XSS) by sending crafted requests to the target application.

## Phase 1 Features

*   **Core HTTP Engine:** Robust request handling using `requests` library, including session management, configurable default headers, timeout, and proxy support.
*   **Configuration Management:** Flexible configuration system supporting:
    *   Hardcoded default settings.
    *   Loading from external YAML configuration files.
    *   Overriding settings via command-line arguments.
*   **SQL Injection (SQLi) Scanner:** Basic error-based SQLi detection for GET parameters.
*   **Cross-Site Scripting (XSS) Scanner:** Basic reflected XSS detection in GET parameters by checking for payload reflection in the response.
*   **Command-Line Interface (CLI):** Allows users to specify target URLs, select scan types (`sqli`, `xss`, `all`), provide a configuration file, define an output file, and override key configuration parameters directly.
*   **Reporting:**
    *   Human-readable console output of findings.
    *   Saving findings to a file in JSON Lines format.

## Project Structure

*   `src/`: Contains the main executable script (`main_scanner.py`), the `core_engine.py`, `config_manager.py`, and `reporter.py`.
*   `modules/`: Houses individual scanner modules, currently including `sqli_scanner.py` and `xss_scanner.py`.
*   `configs/`: Intended for user-defined YAML configuration files. A `sample-config.yaml` is provided as a template.
*   `results/`: Default directory where scan output files (e.g., JSON Lines reports) are saved.
*   `wordlists/`: This directory can be used to store custom wordlists for scanners (e.g., for SQLi payloads, XSS vectors, directory bruteforcing lists if those modules are added). Current scanners use internal, small payload lists.

## Prerequisites

*   Python 3.7+ (developed and tested with Python 3.10).
*   External Python libraries: See `requirements.txt` for a full list (includes `PyYAML` and `requests`).

## Setup / Installation

1.  **Clone the Repository:**
    If you have git installed:
    ```bash
    # git clone <repository_url>
    ```
    Alternatively, download the source code and extract it into a directory named `AdvancedBountyScanner`.

2.  **Navigate to the Project Directory:**
    ```bash
    cd AdvancedBountyScanner
    ```

3.  **Install Required Python Packages:**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **(Optional) Make the Main Script Executable:**
    This allows you to run the script directly without prefixing `python3`.
    ```bash
    chmod +x src/main_scanner.py
    ```
    If you do this, you can run the tool like: `./src/main_scanner.py ...`

## Configuration

AdvancedBountyScanner can be configured through a combination of default settings, a YAML configuration file, and command-line arguments. CLI arguments take the highest precedence.

A sample configuration file is provided at `configs/sample-config.yaml`. You can copy this to `my_config.yaml` (or any other name) in the `configs/` directory (or elsewhere) and customize it.

**Example `configs/sample-config.yaml`:**
```yaml
# AdvancedBountyScanner/configs/sample-config.yaml
# This is a sample configuration file for AdvancedBountyScanner.
# Users can copy this to, for example, 'my_config.yaml' and customize it.

# Default User-Agent string for HTTP requests
user_agent: "MyCustomScanner/1.1 (AdvancedBountyScanner SampleConfig)"

# Default timeout for HTTP requests in seconds
timeout: 15

# Proxy configuration (uncomment and set to use a proxy)
# proxy:
#   http: "http://127.0.0.1:8080"
#   https: "http://127.0.0.1:8080"
  # socks5: "socks5://127.0.0.1:1080" # Example for SOCKS proxy

# Maximum number of concurrent requests (for modules that support concurrency)
max_concurrent_requests: 5

# Rate limit for requests (requests per second, 0 means no limit)
# Note: Actual enforcement depends on module implementation.
rate_limit: 0
```
To use a configuration file, pass its path using the `--config_file` argument.

## Usage

All commands should generally be run from the root of the `AdvancedBountyScanner` project directory.

**Basic Scan (SQLi and XSS on a target URL):**
```bash
python3 src/main_scanner.py http://testphp.vulnweb.com/listproducts.php?cat=1 --scans sqli xss
```

**Run All Available Scans:**
```bash
python3 src/main_scanner.py http://testphp.vulnweb.com/listproducts.php?cat=1 --scans all
```

**Using a Custom Configuration File:**
```bash
python3 src/main_scanner.py http://testphp.vulnweb.com/listproducts.php?cat=1 --scans all --config_file configs/my_custom_config.yaml
```

**Saving Output to a File:**
The output will be saved in JSON Lines format.
```bash
python3 src/main_scanner.py http://testphp.vulnweb.com/listproducts.php?cat=1 --scans all --output_file results/scan_report_vulnweb.jsonl
```

**Overriding a Configuration Setting via CLI:**
This example overrides the default/file timeout to 20 seconds.
```bash
python3 src/main_scanner.py http://testphp.vulnweb.com/listproducts.php?cat=1 --scans sqli --timeout 20
```

**Specifying an HTTP Proxy via CLI:**
```bash
python3 src/main_scanner.py http://example.com --scans sqli --proxy_http "http://127.0.0.1:8080"
```

## Disclaimer

This tool is for educational and authorized testing purposes only. Always obtain explicit permission from the target system's owner before conducting any scanning or testing activities. The developers of this tool are not responsible for any misuse or damage caused by this tool. Use responsibly and ethically.
