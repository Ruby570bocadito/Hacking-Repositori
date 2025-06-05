import socket
import os

# Determine the correct path to the wordlists directory relative to this module
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SUBDOMAIN_WORDLIST = os.path.join(MODULE_DIR, '..', 'wordlists', 'common_subdomains.txt')

def load_wordlist(wordlist_path):
    """Loads a wordlist from the given path, one entry per line."""
    if not os.path.exists(wordlist_path):
        print(f"[!] Wordlist not found: {wordlist_path}")
        return []
    try:
        with open(wordlist_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[!] Error reading wordlist {wordlist_path}: {e}")
        return []

def find_subdomains(domain, wordlist_path=None):
    """
    Finds active subdomains for a given domain using a wordlist.

    Args:
        domain (str): The target domain (e.g., "example.com").
        wordlist_path (str, optional): Path to a custom subdomain wordlist.
                                       Defaults to 'common_subdomains.txt'.

    Returns:
        list: A list of tuples, where each tuple contains (subdomain_full_url, ip_address).
              Returns an empty list if no subdomains are found or if the base domain is invalid.
    """
    if wordlist_path is None:
        wordlist_path = DEFAULT_SUBDOMAIN_WORDLIST
        print(f"[*] Using default subdomain wordlist: {wordlist_path}")

    subdomain_list = load_wordlist(wordlist_path)
    if not subdomain_list:
        # This print is acceptable as it's an early exit / config error
        print(f"[*] No subdomains loaded from wordlist: {wordlist_path}. Aborting subdomain scan.")
        return []

    results = []
    # This print is acceptable as it's informational about the process
    print(f"[*] Scanning for subdomains of {domain} using wordlist: {os.path.basename(wordlist_path)}...")

    for sub in subdomain_list:
        subdomain_url = f"{sub}.{domain}"
        try:
            ip_address = socket.gethostbyname(subdomain_url)
            results.append({'subdomain': subdomain_url, 'ip': ip_address, 'status': 'found'})
        except socket.gaierror:
            results.append({'subdomain': subdomain_url, 'ip': None, 'status': 'not_resolved'})
        except Exception as e:
            results.append({'subdomain': subdomain_url, 'ip': None, 'status': f'error: {e}'})

    return results

def print_results(results, domain):
    """Prints subdomain scan results in a human-readable format."""
    print(f"\n--- Subdomain Scan Results for {domain} ---")
    found_any = False
    if not results:
        print("  No attempts made or wordlist was empty.")
        return

    for res in results:
        if res['status'] == 'found':
            print(f"  [+] Found: {res['subdomain']} -> {res['ip']}")
            found_any = True

    if not found_any:
        print(f"  No active subdomains found for {domain} from the provided list.")
    # Optionally, print not_resolved or errors for verbosity:
    # for res in results:
    #     if res['status'] == 'not_resolved':
    #         print(f"  [-] Not resolved: {res['subdomain']}")
    #     elif 'error' in res['status']:
    #         print(f"  [!] Error for {res['subdomain']}: {res['status']}")


if __name__ == '__main__':
    target_domain_example = "google.com"

    print(f"[*] Example Subdomain Scan for: {target_domain_example}")
    # It's good practice to ensure the base domain itself is resolvable first,
    # though this script focuses on subdomains.
    try:
        socket.gethostbyname(target_domain_example)
    except socket.gaierror:
        print(f"[!] The base domain {target_domain_example} itself could not be resolved. Exiting.")
        exit()
    except Exception as e:
        print(f"[!] An error occurred resolving the base domain {target_domain_example}: {e}")
        exit()

    scan_results = find_subdomains(target_domain_example)
    print_results(scan_results, target_domain_example)
