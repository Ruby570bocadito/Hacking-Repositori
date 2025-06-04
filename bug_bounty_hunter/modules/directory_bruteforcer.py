import requests
from urllib.parse import urlparse, urljoin
import os

# Determine the correct path to the wordlists directory relative to this module
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR_WORDLIST = os.path.join(MODULE_DIR, '..', 'wordlists', 'common_directories.txt')

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

def find_directories(base_url, wordlist_path=None):
    """
    Attempts to find common directories or files on a web server using a wordlist.

    Args:
        base_url (str): The base URL to scan (e.g., "http://example.com").
        wordlist_path (str, optional): Path to a custom directory/file wordlist.
                                       Defaults to 'common_directories.txt'.
    Returns:
        list: A list of URLs that returned a 'successful' status code.
    """
    if wordlist_path is None:
        wordlist_path = DEFAULT_DIR_WORDLIST
        print(f"[*] Using default directory/file wordlist: {wordlist_path}")

    path_list = load_wordlist(wordlist_path)
    if not path_list:
        print(f"[*] No paths loaded from wordlist: {wordlist_path}. Aborting directory bruteforce.")
        return []

    found_urls = []

    print(f"[*] Bruteforcing directories and files for {base_url} using wordlist: {os.path.basename(wordlist_path)}...")

    # Validate base_url
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"[!] Invalid base URL: {base_url}. Please include http/https.")
        return []

    # Define what we consider a "successful" status code (not just 200)
    # 200: OK
    # 204: No Content (still indicates resource might exist or action was successful)
    # 301: Moved Permanently (indicates resource exists, just elsewhere)
    # 302: Found (Temporary Redirect, resource exists)
    # 307: Temporary Redirect (similar to 302)
    # 401: Unauthorized (resource exists but needs auth)
    # 403: Forbidden (resource exists but access is denied)
    # 405: Method Not Allowed (resource exists but GET might not be the way, still indicates presence)
    successful_status_codes = [200, 204, 301, 302, 307, 401, 403, 405]

    # Use a session for potentially better performance (connection pooling)
    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 BugBountyHunterTool/1.0'})

        for path in path_list: # Iterate over paths from the wordlist
            # Ensure path is not absolute and join correctly
            if path.startswith('/'):
                path = path[1:]

            # Using urljoin to correctly handle slashes
            test_url = urljoin(base_url + ('/' if not base_url.endswith('/') else ''), path)

            try:
                response = session.get(test_url, timeout=5, allow_redirects=False) # allow_redirects=False to see original status
                if response.status_code in successful_status_codes:
                    print(f"[+] Found: {test_url} (Status: {response.status_code})")
                    found_urls.append(test_url)
                # else:
                    # Optionally print misses for verbosity
                    # print(f"[-] Miss: {test_url} (Status: {response.status_code})")

            except requests.exceptions.RequestException as e:
                # E.g., ConnectionError, Timeout, TooManyRedirects
                print(f"[!] Error connecting to {test_url}: {type(e).__name__}")
            except Exception as e:
                print(f"[!] An unexpected error occurred with {test_url}: {e}")

    return found_urls

if __name__ == '__main__':
    # Example usage:
    # Using a public domain that is likely to have some of these paths.
    # Be mindful and responsible when choosing targets.
    # "http://scanme.nmap.org" is a good candidate for testing.
    # For a wider range of results, one might test against a self-hosted vulnerable app.

    # target_url = "http://scanme.nmap.org"
    # scanme.nmap.org doesn't have many of these common paths, let's use a different example
    # that is more likely to have some common files like robots.txt
    target_url = "http://google.com" # Many sites have robots.txt or sitemap.xml

    if not target_url.startswith(('http://', 'https://')):
        print("[!] Please provide a full URL including http:// or https://")
        exit()

    print(f"[*] Starting directory and file bruteforce on {target_url}")

    discovered_paths = find_directories(target_url)

    if discovered_paths:
        print("\n[*] Summary of discovered paths:")
        for url_path in discovered_paths:
            print(url_path)
    else:
        print(f"\n[*] No common directories or files found for {target_url} from the predefined list, or an error occurred.")
