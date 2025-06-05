import requests
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 BugBountyHunterTool/1.0'
REQUEST_TIMEOUT = 10

def _ensure_url_scheme(url_input):
    """Ensures the URL has a scheme, defaulting to http:// if none is present."""
    if not url_input:
        return ""
    parsed_url = urlparse(url_input)
    if not parsed_url.scheme:
        return "http://" + url_input
    return url_input

def _fetch_url_content(url):
    """Fetches content for a given URL."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()
        return response.text, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None, f"Not found (404): {url}"
        return None, f"HTTP error for {url}: {e}"
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching {url}: {e}"

def _parse_robots_txt(content, base_url):
    """Parses robots.txt content."""
    directives = {}
    sitemap_urls_from_robots = []
    current_user_agent = None

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split(':', 1)
        if len(parts) != 2:
            continue

        key, value = parts[0].strip().lower(), parts[1].strip()

        if key == 'user-agent':
            current_user_agent = value
            if current_user_agent not in directives:
                directives[current_user_agent] = {"Allow": [], "Disallow": []}
        elif key == 'allow' and current_user_agent:
            directives[current_user_agent]["Allow"].append(value)
        elif key == 'disallow' and current_user_agent:
            directives[current_user_agent]["Disallow"].append(value)
        elif key == 'sitemap':
            sitemap_urls_from_robots.append(value)

    return directives, sitemap_urls_from_robots

def _parse_sitemap_xml(xml_content, sitemap_url_for_log=""):
    """Parses a sitemap XML content and returns a list of URLs and nested sitemap URLs."""
    urls = []
    nested_sitemaps = []
    try:
        root = ET.fromstring(xml_content)
        # XML namespace is common in sitemaps
        namespace = ''
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'

        for url_element in root.findall(f'{namespace}url'):
            loc_element = url_element.find(f'{namespace}loc')
            if loc_element is not None and loc_element.text:
                urls.append(loc_element.text.strip())

        for sitemap_index_element in root.findall(f'{namespace}sitemap'):
            loc_element = sitemap_index_element.find(f'{namespace}loc')
            if loc_element is not None and loc_element.text:
                nested_sitemaps.append(loc_element.text.strip())

    except ET.ParseError as e:
        return [], [], f"XML ParseError for {sitemap_url_for_log}: {e}"
    return urls, nested_sitemaps, None


def analyze_robots_sitemap(base_url):
    """
    Analyzes robots.txt and sitemap.xml for a given base URL.
    """
    base_url = _ensure_url_scheme(base_url)
    results = {
        "robots_txt_found": False,
        "robots_txt_url": None,
        "robots_txt_content": None,
        "directives": {},
        "sitemap_urls_from_robots": [],
        "sitemaps_processed": [], # List of sitemap URLs that were actually fetched and parsed
        "sitemap_urls_parsed": set(), # Using a set to store unique URLs then convert to list
        "errors": []
    }

    # 1. Analyze robots.txt
    # Informational print, acceptable
    print(f"[*] Analyzing robots.txt for {base_url}...")
    robots_url = urljoin(base_url, "/robots.txt")
    results["robots_txt_url"] = robots_url
    robots_content, error = _fetch_url_content(robots_url)

    if error:
        results["errors"].append(error)
    elif robots_content:
        results["robots_txt_found"] = True
        # results["robots_txt_content"] = robots_content # Storing raw content can be very large, optional for JSON
        directives, sitemap_urls_from_robots = _parse_robots_txt(robots_content, base_url)
        results["directives"] = directives
        results["sitemap_urls_from_robots"] = sitemap_urls_from_robots

    # 2. Analyze Sitemaps
    # Informational print, acceptable
    print(f"[*] Analyzing sitemaps for {base_url}...")
    sitemaps_to_process = list(results["sitemap_urls_from_robots"])

    # Try common sitemap.xml if no sitemaps found in robots.txt or if explicitly desired
    default_sitemap_url = urljoin(base_url, "/sitemap.xml")
    if default_sitemap_url not in sitemaps_to_process: # Avoid duplicate processing if already listed
        sitemaps_to_process.append(default_sitemap_url) # Add it to the queue

    processed_sitemap_log = set()

    queue = list(sitemaps_to_process)
    while queue:
        sitemap_url = queue.pop(0).strip()
        if not sitemap_url or sitemap_url in processed_sitemap_log: # Ensure URL is not empty and not reprocessed
            continue

        # Informational print for each sitemap being processed
        print(f"  [*] Processing sitemap: {sitemap_url}")
        processed_sitemap_log.add(sitemap_url)
        # results["sitemaps_processed"].append(sitemap_url) # Redundant if using processed_sitemap_log for this info

        sitemap_content, error = _fetch_url_content(sitemap_url)
        if error:
            results["errors"].append(error)
            # If a default sitemap (like /sitemap.xml) was not found, don't add it to processed list
            # unless it was explicitly listed in robots.txt
            if sitemap_url == default_sitemap_url and default_sitemap_url not in results["sitemap_urls_from_robots"]:
                pass # Don't log default sitemap.xml as "processed" if it just 404'd and wasn't in robots
            else:
                 results["sitemaps_processed"].append(sitemap_url) # Log it as processed even if error, if from robots
            continue

        # If content was fetched, it means the sitemap URL was valid, so add to processed list
        results["sitemaps_processed"].append(sitemap_url)

        if sitemap_content:
            urls, nested_sitemaps, parse_error = _parse_sitemap_xml(sitemap_content, sitemap_url)
            if parse_error:
                results["errors"].append(parse_error)
            results["sitemap_urls_parsed"].update(urls)
            for nested_sitemap in nested_sitemaps:
                # Ensure full URL for nested sitemaps if they are relative
                absolute_nested_sitemap_url = urljoin(base_url, nested_sitemap.strip())
                if absolute_nested_sitemap_url not in processed_sitemap_log and absolute_nested_sitemap_url not in queue:
                    queue.append(absolute_nested_sitemap_url)

    results["sitemap_urls_parsed"] = sorted(list(results["sitemap_urls_parsed"]))
    # Remove duplicates from sitemaps_processed just in case, though set logic should handle it
    results["sitemaps_processed"] = sorted(list(set(results["sitemaps_processed"])))
    return results


def print_results(results, base_url_unused): # base_url_unused as it's part of results logic now
    """Prints robots.txt and sitemap analysis results."""
    print(f"\n--- Robots.txt & Sitemap Analysis Results for {results.get('robots_txt_url', '').rsplit('/', 1)[0]} ---")

    print("\n  --- Robots.txt Analysis ---")
    print(f"    URL: {results['robots_txt_url']}")
    print(f"    Found: {results['robots_txt_found']}")
    if results['robots_txt_found']:
        if results['directives']:
            print("    Directives:")
            for agent, rules in results['directives'].items():
                print(f"      User-agent: {agent}")
                if rules.get("Allow"): print(f"        Allow: {rules['Allow']}")
                if rules.get("Disallow"): print(f"        Disallow: {rules['Disallow']}")
        else:
            print("    (No directives parsed or robots.txt was empty of directives)")
        print(f"    Sitemap URLs from robots.txt: {results['sitemap_urls_from_robots']}")

    print("\n  --- Sitemap Analysis ---")
    if results['sitemaps_processed']:
        print(f"    Sitemaps Processed ({len(results['sitemaps_processed'])}):")
        for sm_url in results['sitemaps_processed']:
            print(f"      - {sm_url}")
    else:
        print("    No sitemaps were found or processed successfully (or listed in robots.txt).")

    if results['sitemap_urls_parsed']:
        print(f"\n    Total Unique URLs extracted from sitemaps ({len(results['sitemap_urls_parsed'])}):")
        limit_print = 20
        for i, url in enumerate(results['sitemap_urls_parsed']):
            if i < limit_print: print(f"      - {url}")
            elif i == limit_print:
                print(f"      ... and {len(results['sitemap_urls_parsed']) - limit_print} more URLs.")
                break
    else:
        print("    No URLs extracted from sitemaps.")

    if results['errors']:
        print("\n  --- Errors Encountered ---")
        for err in results['errors']:
            print(f"    - {err}")

    print("\n[*] Robots/Sitemap analysis complete.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python robots_sitemap_analyzer.py <base_URL>")
        print("Example: python robots_sitemap_analyzer.py https://google.com")
        sys.exit(1)

    target_base_url_example = sys.argv[1]

    # print(f"[*] Analyzing robots.txt and sitemaps for: {target_base_url_example}\n") # Now handled in main func

    analysis_data_rs = analyze_robots_sitemap(target_base_url_example)
    print_results(analysis_data_rs, target_base_url_example) # Second arg not used by print_results
