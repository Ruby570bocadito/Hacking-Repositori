#!/usr/bin/env python3

import argparse
import os
import sys
import json # For pretty printing results

# --- Path Setup ---
def setup_module_paths():
    """
    Adjusts sys.path to allow importing modules from 'src' and 'modules' directories
    assuming this script (main_scanner.py) is in the 'src' directory,
    and 'modules' is a sibling to 'src'.
    """
    # Path to the 'src' directory (where this script is)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Path to the project root ('AdvancedBountyScanner')
    project_root = os.path.dirname(src_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root) # Allows 'from modules import ...'

# Call path setup early
setup_module_paths()

# --- Imports after path setup ---
try:
    from core_engine import CoreEngine
    from config_manager import ConfigManager
    from reporter import Reporter # Import the new Reporter class
    from modules.sqli_scanner import SQLiScanner
    from modules.xss_scanner import XSSScanner
    # Import other scanner modules here as they are created
except ImportError as e:
    print(f"[!] Critical Error: Failed to import necessary modules: {e}", file=sys.stderr)
    print(f"    Current sys.path: {sys.path}", file=sys.stderr)
    print(f"    Please ensure the script is run from the 'src' directory or the project root,", file=sys.stderr)
    print(f"    and that all modules are in their correct locations ('src' and 'modules').", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Advanced Bounty Scanner - A modular web vulnerability scanner.")

    # Target and Scan Types
    parser.add_argument("target_url", help="The base URL to scan (e.g., http://example.com/page.php?id=1).")
    parser.add_argument(
        "--scans",
        nargs='+',
        required=True,
        choices=['sqli', 'xss', 'all'], # Add more choices as scanners are added
        help="Types of scans to perform (e.g., sqli xss). 'all' runs all available scans."
    )

    # Configuration File
    parser.add_argument(
        "--config_file",
        help="Path to a custom YAML configuration file."
    )
    parser.add_argument(
        "--output_file",
        help="Path to save the scan results (e.g., results.json). (Currently prints to console)"
    )

    # Common Config Overrides (mirroring some ConfigManager defaults)
    parser.add_argument("--user_agent", help="Override the default User-Agent.")
    parser.add_argument("--timeout", type=int, help="Override the default request timeout in seconds.")
    parser.add_argument("--proxy_http", help="HTTP Proxy (e.g., http://127.0.0.1:8080).")
    parser.add_argument("--proxy_https", help="HTTPS Proxy (e.g., http://127.0.0.1:8080 or socks5://127.0.0.1:1080).")
    parser.add_argument("--rate_limit", type=float, help="Set requests per second (0 for no limit).")
    parser.add_argument("--max_concurrent_requests", type=int, help="Set max concurrent requests.")

    args = parser.parse_args()

    # --- Initialize ConfigManager ---
    config_manager = ConfigManager(default_config_path=args.config_file if args.config_file else None)

    # Apply CLI overrides to ConfigManager
    if args.user_agent:
        config_manager.update_setting('user_agent', args.user_agent)
    if args.timeout is not None: # Check for None as 0 is a valid timeout (though impractical)
        config_manager.update_setting('timeout', args.timeout)

    cli_proxies = {}
    if args.proxy_http:
        cli_proxies['http'] = args.proxy_http
    if args.proxy_https:
        cli_proxies['https'] = args.proxy_https
    if cli_proxies:
        # If proxy settings already exist (e.g. from file), merge carefully or decide to overwrite.
        # For CLI, usually overwrite is intended for simplicity here.
        existing_proxies = config_manager.get_setting('proxy', {})
        if existing_proxies is None: existing_proxies = {} # Ensure it's a dict
        existing_proxies.update(cli_proxies)
        config_manager.update_setting('proxy', existing_proxies if existing_proxies else None)

    if args.rate_limit is not None:
        config_manager.update_setting('rate_limit', args.rate_limit)
    if args.max_concurrent_requests is not None:
        config_manager.update_setting('max_concurrent_requests', args.max_concurrent_requests)

    print("[*] Effective Configuration:")
    print(f"  User-Agent: {config_manager.get_setting('user_agent')}")
    print(f"  Timeout: {config_manager.get_setting('timeout')}")
    print(f"  Proxy: {config_manager.get_setting('proxy')}")
    print(f"  Rate Limit: {config_manager.get_setting('rate_limit')}")
    print(f"  Max Concurrent Requests: {config_manager.get_setting('max_concurrent_requests')}")


    # --- Initialize CoreEngine ---
    core_engine = CoreEngine(
        default_headers={'User-Agent': config_manager.get_setting('user_agent')},
        proxy=config_manager.get_setting('proxy'),
        timeout=config_manager.get_setting('timeout')
    )

    # --- Initialize Scanners ---
    # (Consider making this more dynamic if many scanners are added)
    sqli_scanner = SQLiScanner(core_engine, config_manager)
    xss_scanner = XSSScanner(core_engine, config_manager)
    # ... initialize other scanners

    all_findings = []
    scans_to_run = args.scans
    if 'all' in scans_to_run:
        scans_to_run = ['sqli', 'xss'] # Expand 'all' to all known scan types

    print(f"\n[*] Target URL: {args.target_url}")
    print(f"[*] Scans to perform: {', '.join(scans_to_run)}\n")

    # --- Run Scans ---
    if 'sqli' in scans_to_run:
        print("--- Starting SQLi Scan ---")
        sqli_findings = sqli_scanner.scan_url(args.target_url)
        if sqli_findings:
            all_findings.extend(sqli_findings)
        print("--- SQLi Scan Finished ---\n")

    if 'xss' in scans_to_run:
        print("--- Starting XSS Scan ---")
        xss_findings = xss_scanner.scan_url(args.target_url)
        if xss_findings:
            all_findings.extend(xss_findings)
        print("--- XSS Scan Finished ---\n")

    # Add other scans here

    # --- Initialize Reporter ---
    reporter = Reporter(config_manager)

    # --- Reporting ---
    if all_findings:
        reporter.print_console(all_findings)
        if args.output_file:
            reporter.save_to_file(all_findings, args.output_file)
    else:
        print("\n[*] No vulnerabilities found with the selected scans.")

    print("\n[*] Advanced Bounty Scanner finished.")


if __name__ == '__main__':
    main()
