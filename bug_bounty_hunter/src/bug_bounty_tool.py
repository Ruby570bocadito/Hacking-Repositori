#!/usr/bin/env python3
import argparse
import os
import sys
from urllib.parse import urlparse

# Adjust path to import modules
# Get the directory of the current script (src/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of script_dir (bug_bounty_hunter/)
base_dir = os.path.dirname(script_dir)
# Construct the path to the modules directory
modules_dir = os.path.join(base_dir, 'modules')
sys.path.append(modules_dir)

try:
    import subdomain_scanner
    import port_scanner
    import directory_bruteforcer
    import wayback_urls
    import header_analyzer
    import robots_sitemap_analyzer
except ImportError as e:
    print(f"[!] Error importing modules: {e}")
    print(f"    Ensure modules are present in: {modules_dir}")
    print(f"    And that all their dependencies are installed (e.g., 'requests').")
    sys.exit(1)

def get_domain_from_target(target_input):
    """Extracts domain name from a URL or returns the input if it's likely a domain already."""
    if not target_input:
        return ""

    parsed_url = urlparse(target_input)
    if parsed_url.scheme and parsed_url.netloc: # If it's a full URL like http://example.com/path
        return parsed_url.netloc
    elif parsed_url.netloc: # If it's like example.com/path (parsed as path by urlparse if no scheme)
        return parsed_url.netloc
    elif parsed_url.path and not parsed_url.scheme: # If it's like example.com (parsed as path if no scheme)
         # Check if it contains common TLDs, crude but better than nothing
        if '.' in parsed_url.path.split('/')[0]:
             return parsed_url.path.split('/')[0]
    return target_input # Assume it's a domain if none of the above

def ensure_url_scheme(target_input):
    """Ensures the URL has a scheme, defaulting to http:// if none is present."""
    if not target_input:
        return ""
    parsed_url = urlparse(target_input)
    if not parsed_url.scheme:
        # If it looks like a common domain (e.g. contains '.'), prepend http
        if '.' in target_input:
            return "http://" + target_input
        else: # Could be localhost or an IP without scheme, also benefits from http
            return "http://" + target_input
    return target_input

def main():
    parser = argparse.ArgumentParser(description="Bug Bounty Automation Tool")
    parser.add_argument("target", help="Target domain or IP address. For 'dir' scan, a base URL is preferred (e.g., http://example.com).")
    parser.add_argument(
        "--scans",
        nargs='+',  # Accepts one or more arguments
        required=True,
        choices=['subdomain', 'port', 'dir', 'wayback', 'header', 'robots', 'all'],
        help="Types of scans to perform (e.g., subdomain port dir wayback header robots or all)."
    )
    parser.add_argument(
        "--subdomain_wordlist",
        help="Path to a custom wordlist for subdomain scanning."
    )
    parser.add_argument(
        "--dir_wordlist",
        help="Path to a custom wordlist for directory bruteforcing."
    )
    parser.add_argument(
        "--output_dir",
        default=os.path.join(base_dir, 'reports'), # Corrected default path
        help="Directory to save reports (used for JSON output if filename not full path)."
    )
    parser.add_argument(
        "--json_output",
        help="File path to save all scan results in JSON format. If a filename without path is given, it's saved in --output_dir."
    )

    args = parser.parse_args()
    target = args.target.strip()
    scans_to_run = args.scans
    json_output_file = args.json_output

    all_scan_results = {} # Initialize for JSON output

    if not target:
        print("[!] Target cannot be empty.")
        parser.print_help()
        sys.exit(1)

    # Expand 'all' scan type
    if 'all' in scans_to_run:
        scans_to_run = ['subdomain', 'port', 'dir', 'wayback', 'header', 'robots']
    scans_to_run = sorted(list(set(scans_to_run))) # Remove duplicates and sort

    # Create reports directory if it doesn't exist and JSON output is specified
    if json_output_file:
        output_directory = args.output_dir
        if not os.path.isabs(json_output_file): # If filename is relative
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
                print(f"[*] Created reports directory: {output_directory}")
            json_output_file = os.path.join(output_directory, json_output_file)


    print(f"[*] Target: {target}")
    print(f"[*] Scans to run: {', '.join(scans_to_run)}")
    if json_output_file:
        print(f"[*] JSON output will be saved to: {json_output_file}")


    if 'subdomain' in scans_to_run:
        # Informational header still useful for console, even if JSON is primary output
        print("\n\n" + "="*20 + " Subdomain Scan Initiated " + "="*20)
        domain_for_subdomain = get_domain_from_target(target)
        if not domain_for_subdomain:
            err_msg = f"[!] Could not reliably determine domain from target '{target}' for subdomain scan."
            print(err_msg)
            if json_output_file: all_scan_results['subdomain_scan'] = {'error': err_msg, 'domain': target, 'results': []}
        else:
            sub_results = subdomain_scanner.find_subdomains(domain_for_subdomain, wordlist_path=args.subdomain_wordlist)
            if json_output_file: all_scan_results['subdomain_scan'] = {'domain': domain_for_subdomain, 'results': sub_results}
            else: subdomain_scanner.print_results(sub_results, domain_for_subdomain)
        if not json_output_file: print("="*20 + " Subdomain Scan Finished " + "="*21 + "\n")


    if 'port' in scans_to_run:
        print("\n\n" + "="*20 + " Port Scan Initiated " + "="*20)
        host_for_portscan = get_domain_from_target(target)
        if not host_for_portscan:
            err_msg = f"[!] Could not reliably determine host from target '{target}' for port scan."
            print(err_msg)
            if json_output_file: all_scan_results['port_scan'] = {'target': target, 'error': err_msg, 'results': []}
        else:
            port_results = port_scanner.scan_ports(host_for_portscan) # Using default ports list in module
            if json_output_file: all_scan_results['port_scan'] = {'target': host_for_portscan, 'results': port_results}
            else: port_scanner.print_results(port_results, host_for_portscan)
        if not json_output_file: print("="*20 + " Port Scan Finished " + "="*23 + "\n")

    if 'dir' in scans_to_run:
        print("\n\n" + "="*20 + " Directory Bruteforce Initiated " + "="*20)
        url_for_dir = ensure_url_scheme(target)
        if not url_for_dir:
            err_msg = f"[!] Could not reliably determine URL from target '{target}' for directory bruteforce."
            print(err_msg)
            if json_output_file: all_scan_results['directory_bruteforce'] = {'target_url': target, 'error': err_msg, 'results': []}
        else:
            dir_results = directory_bruteforcer.find_directories(url_for_dir, wordlist_path=args.dir_wordlist)
            if json_output_file: all_scan_results['directory_bruteforce'] = {'target_url': url_for_dir, 'results': dir_results}
            else: directory_bruteforcer.print_results(dir_results, url_for_dir)
        if not json_output_file: print("="*20 + " Directory Bruteforce Finished " + "="*19 + "\n")

    if 'wayback' in scans_to_run:
        print("\n\n" + "="*20 + " Wayback URLs Scan Initiated " + "="*20)
        domain_for_wayback = get_domain_from_target(target)
        if not domain_for_wayback:
            err_msg = f"[!] Could not reliably determine domain from target '{target}' for Wayback URLs scan."
            print(err_msg)
            if json_output_file: all_scan_results['wayback_urls_scan'] = {'domain': target, 'error': err_msg, 'results': {}}
        else:
            wayback_results_dict = wayback_urls.get_wayback_urls(domain_for_wayback)
            if json_output_file: all_scan_results['wayback_urls_scan'] = wayback_results_dict # Already a dict
            else: wayback_urls.print_results(wayback_results_dict, domain_for_wayback) # Second arg unused
        if not json_output_file: print("="*20 + " Wayback URLs Scan Finished " + "="*20 + "\n")

    if 'header' in scans_to_run:
        print("\n\n" + "="*20 + " HTTP Header Analysis Initiated " + "="*20)
        url_for_header = ensure_url_scheme(target)
        if not url_for_header:
            err_msg = f"[!] Could not reliably determine URL from target '{target}' for Header Analysis."
            print(err_msg)
            if json_output_file: all_scan_results['header_analysis'] = {'target_url': target, 'error': err_msg, 'results': {}}
        else:
            header_results_dict = header_analyzer.analyze_headers(url_for_header)
            if json_output_file: all_scan_results['header_analysis'] = header_results_dict # Already a dict
            else: header_analyzer.print_results(header_results_dict, url_for_header) # Second arg unused
        if not json_output_file: print("="*20 + " HTTP Header Analysis Finished " + "="*19 + "\n")

    if 'robots' in scans_to_run:
        print("\n\n" + "="*20 + " Robots.txt & Sitemap Analysis Initiated " + "="*20)
        url_for_robots_base = ensure_url_scheme(target)
        if not url_for_robots_base:
            err_msg = f"[!] Could not reliably determine URL from target '{target}' for Robots/Sitemap Analysis."
            print(err_msg)
            if json_output_file: all_scan_results['robots_sitemap_analysis'] = {'target_url': target, 'error': err_msg, 'results': {}}
        else:
            parsed_url_for_robots = urlparse(url_for_robots_base)
            base_url_for_robots = f"{parsed_url_for_robots.scheme}://{parsed_url_for_robots.netloc}"

            robots_results_dict = robots_sitemap_analyzer.analyze_robots_sitemap(base_url_for_robots)
            if json_output_file: all_scan_results['robots_sitemap_analysis'] = robots_results_dict # Already a dict
            else: robots_sitemap_analyzer.print_results(robots_results_dict, base_url_for_robots) # Second arg unused
        if not json_output_file: print("="*20 + " Robots.txt & Sitemap Analysis Finished " + "="*13 + "\n")

    # Save all results to JSON if path specified
    if json_output_file:
        try:
            import json # Ensure json is imported
            with open(json_output_file, 'w') as f:
                json.dump(all_scan_results, f, indent=4)
            print(f"\n[+] All scan results saved to {json_output_file}")
        except Exception as e:
            print(f"\n[!] Error saving JSON output to {json_output_file}: {e}")

    print("\n[*] All selected scans completed.")

if __name__ == "__main__":
    # Ensure the script is run from the 'bug_bounty_hunter' directory or adjust paths accordingly
    # For simplicity, this script assumes it can find the 'modules' directory relative to its own location.
    main()
