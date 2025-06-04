import requests
import json

def get_wayback_urls(domain):
    """
    Fetches unique URLs for a given domain from the Wayback Machine CDX API.

    Args:
        domain (str): The target domain (e.g., "example.com").

    Returns:
        list: A list of unique URLs (strings) found. Returns an empty list on error or if no URLs are found.
    """
    print(f"[*] Fetching Wayback Machine URLs for *.{domain}...")

    # Construct the CDX API URL
    # url=*.example.com/* : Search for all subdomains and paths
    # output=json : Request JSON output
    # fl=original : Fetch the 'original' field (the URL)
    # collapse=urlkey : Collapse results on the urlkey to get unique URLs
    # limit=1000 : Limit the number of results to avoid extremely large responses (optional)
    cdx_api_url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey&limit=1000"

    found_urls = set() # Use a set to store unique URLs initially

    try:
        response = requests.get(cdx_api_url, timeout=30) # Increased timeout to 30 seconds
        response.raise_for_status()  # Raise HTTPError for bad responses (4XX or 5XX)

        # The response is a list of lists in JSON, e.g., [["original"], ["http://example.com/path1"], ...]
        # The first item is often the header, so we skip it.
        data = response.json()

        if not data or len(data) <= 1:
            print(f"[-] No results found for {domain} in the Wayback Machine.")
            return []

        # Skip the header row (e.g., ["original"])
        for item in data[1:]:
            if item and isinstance(item, list) and len(item) > 0:
                found_urls.add(item[0])

        if not found_urls:
            print(f"[-] No URLs extracted though data was received for {domain}.")
            return []

        print(f"[+] Found {len(found_urls)} unique URLs.")
        return sorted(list(found_urls)) # Return as a sorted list

    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP error while fetching Wayback URLs for {domain}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"[!] Connection error while fetching Wayback URLs for {domain}: {e}")
    except requests.exceptions.Timeout:
        print(f"[!] Timeout while fetching Wayback URLs for {domain}.")
    except json.JSONDecodeError:
        print(f"[!] Error decoding JSON response from Wayback Machine for {domain}. The response might not be valid JSON.")
        print(f"    Raw response text (first 200 chars): {response.text[:200]}")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")

    return []

if __name__ == '__main__':
    # Example usage:
    # Using a domain known to have a history.
    # target_domain = "example.com"
    # For a more extensive list, you could try "google.com", but be mindful of the output size.
    target_domain = "nmap.org" # Testing with nmap.org

    print(f"[*] Starting Wayback Machine URL fetch for {target_domain}")

    urls_from_wayback = get_wayback_urls(target_domain)

    if urls_from_wayback:
        print(f"\n[*] Summary of unique URLs found for {target_domain}:")
        for url in urls_from_wayback:
            print(url)
    else:
        print(f"\n[*] No URLs found for {target_domain} via Wayback Machine, or an error occurred.")
