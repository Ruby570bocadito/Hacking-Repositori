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
        print(f"[*] No subdomains loaded from wordlist: {wordlist_path}. Aborting subdomain scan.")
        return []

    found_subdomains = []

    print(f"[*] Scanning for subdomains of {domain} using wordlist: {os.path.basename(wordlist_path)}...")

    for sub in subdomain_list:
        subdomain_url = f"{sub}.{domain}"
        try:
            ip_address = socket.gethostbyname(subdomain_url)
            print(f"[+] Found: {subdomain_url} -> {ip_address}")
            found_subdomains.append((subdomain_url, ip_address))
        except socket.gaierror:
            # socket.gaierror means the address-related error occurred, e.g., name not resolved
            print(f"[-] Not found or could not resolve: {subdomain_url}")
        except Exception as e:
            print(f"[!] An error occurred while checking {subdomain_url}: {e}")

    return found_subdomains

if __name__ == '__main__':
    # Example usage:
    # Note: Replace "example.com" with a domain you have permission to test,
    # or a domain you own. For demonstration, this might not resolve all subdomains.
    # Using a public domain like "google.com" for a more likely successful demonstration.
    target_domain = "google.com"

    # It's good practice to ensure the base domain itself is resolvable first,
    # though this script focuses on subdomains.
    try:
        socket.gethostbyname(target_domain)
    except socket.gaierror:
        print(f"[!] The base domain {target_domain} itself could not be resolved. Exiting.")
        exit()
    except Exception as e:
        print(f"[!] An error occurred resolving the base domain {target_domain}: {e}")
        exit()

    active_subdomains = find_subdomains(target_domain)

    if active_subdomains:
        print("\n[*] Summary of found subdomains:")
        for sub_url, ip in active_subdomains:
            print(f"{sub_url}: {ip}")
    else:
        print("\n[*] No subdomains found from the predefined list.")
