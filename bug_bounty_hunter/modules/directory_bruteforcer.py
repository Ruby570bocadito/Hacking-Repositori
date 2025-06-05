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
        # Informational print, acceptable
        print(f"[*] No paths loaded from wordlist: {wordlist_path}. Aborting directory bruteforce.")
        return []

    results = []
    # Informational print, acceptable
    print(f"[*] Bruteforcing directories and files for {base_url} using wordlist: {os.path.basename(wordlist_path)}...")

    parsed_url = urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        # Informational print, acceptable as it's a config error
        print(f"[!] Invalid base URL: {base_url}. Please include http/https.")
        return [{'url': base_url, 'status_code': None, 'error_message': 'Invalid base URL format.'}]

    successful_status_codes = [200, 204, 301, 302, 307, 401, 403, 405]

    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 BugBountyHunterTool/1.0'})

        for path_item in path_list:
            current_path = path_item.strip()
            if not current_path:
                continue
            if current_path.startswith('/'): # Ensure relative path
                current_path = current_path[1:]

            test_url = urljoin(base_url + ('/' if not base_url.endswith('/') else ''), current_path)

            try:
                response = session.get(test_url, timeout=5, allow_redirects=False)
                if response.status_code in successful_status_codes:
                    results.append({'url': test_url, 'status_code': response.status_code})
                # Optionally include misses or all attempts in results for more comprehensive JSON
                # else:
                #     results.append({'url': test_url, 'status_code': response.status_code, 'status': 'miss'})

            except requests.exceptions.RequestException as e:
                results.append({'url': test_url, 'status_code': None, 'error_message': type(e).__name__})
            except Exception as e: # Should be rare
                results.append({'url': test_url, 'status_code': None, 'error_message': f"Unexpected error: {e}"})

    return results

def print_results(results, base_url):
    """Prints directory bruteforce results in a human-readable format."""
    print(f"\n--- Directory Bruteforce Results for {base_url} ---")

    if not results:
        print("  No paths were attempted (e.g., empty wordlist or initial error).")
        return

    if results[0].get('error_message') == 'Invalid base URL format.':
        print(f"  [!] Error: {results[0]['error_message']} for URL '{results[0]['url']}'")
        return

    found_any = False
    for res in results:
        if 'error_message' in res:
            # print(f"  [!] Error for {res['url']}: {res['error_message']}") # Optional: for verbosity
            pass
        elif res.get('status_code') is not None: # Check if it's not an error entry without status code
            print(f"  [+] Found: {res['url']} (Status: {res['status_code']})")
            found_any = True

    if not found_any:
        print(f"  No accessible directories or files found for {base_url} from the provided list.")

if __name__ == '__main__':
    target_url_example = "http://google.com"

    if not target_url_example.startswith(('http://', 'https://')):
        print("[!] Please provide a full URL including http:// or https:// for testing.")
        exit()

    print(f"[*] Example Directory Bruteforce for: {target_url_example}")
    scan_results = find_directories(target_url_example)
    print_results(scan_results, target_url_example)
