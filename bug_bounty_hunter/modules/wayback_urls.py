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

    extracted_urls_set = set()
    error_message = None
    raw_response_snippet = None

    # Informational print, acceptable
    print(f"[*] Fetching Wayback Machine URLs for *.{domain}...")

    try:
        response = requests.get(cdx_api_url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data or len(data) <= 1:
            error_message = f"No results found for {domain} in the Wayback Machine (empty or header-only response)."
        else:
            for item in data[1:]: # Skip header row
                if item and isinstance(item, list) and len(item) > 0:
                    extracted_urls_set.add(item[0])

            if not extracted_urls_set:
                 error_message = f"No URLs extracted though data was received for {domain}."
            else:
                # This print is acceptable as it's a summary before returning
                print(f"[+] Found {len(extracted_urls_set)} unique URLs from Wayback Machine for {domain}.")


    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP error: {e}"
    except requests.exceptions.ConnectionError as e:
        error_message = f"Connection error: {e}"
    except requests.exceptions.Timeout:
        error_message = "Timeout during request."
    except json.JSONDecodeError as e_json:
        error_message = f"JSON decode error: {e_json}."
        # Try to get response text if available
        try:
            raw_response_snippet = response.text[:200] if 'response' in locals() else "Response object not available."
        except Exception: # Catch any issue trying to get response text
            raw_response_snippet = "Could not retrieve raw response snippet."
    except Exception as e:
        error_message = f"Unexpected error: {e}"

    # Prepare results dictionary
    results_dict = {
        'domain': domain,
        'urls': sorted(list(extracted_urls_set)),
        'count': len(extracted_urls_set),
        'error': error_message,
        'raw_response_snippet': raw_response_snippet # Only populated on JSONDecodeError
    }
    return results_dict


def print_results(results, domain_unused): # domain_unused as it's already in results dict
    """Prints Wayback URL scan results in a human-readable format."""
    print(f"\n--- Wayback Machine URL Results for {results['domain']} ---")

    if results['error']:
        print(f"  [!] Error: {results['error']}")
        if results['raw_response_snippet']:
            print(f"      Raw response snippet: {results['raw_response_snippet']}")

    if results['urls']:
        print(f"  Found {results['count']} unique URLs:")
        # Limit printing for brevity in console
        limit_print = 20
        for i, url in enumerate(results['urls']):
            if i < limit_print:
                print(f"    - {url}")
            elif i == limit_print:
                print(f"    ... and {results['count'] - limit_print} more URLs.")
                break
    elif not results['error']: # No error but no URLs
        print("  No URLs found.")


if __name__ == '__main__':
    target_domain_example = "nmap.org"

    print(f"[*] Example Wayback Machine URL Fetch for: {target_domain_example}")
    scan_results = get_wayback_urls(target_domain_example)
    print_results(scan_results, target_domain_example) # Second arg is technically not used by this print_results
