import requests
import sys
import argparse
import json # For pretty printing the dict in main, if desired

SECURITY_HEADERS_TO_CHECK = [
    'Content-Security-Policy',
    'Strict-Transport-Security',
    'X-Frame-Options',
    'X-Content-Type-Options',
    'Referrer-Policy',
    'Permissions-Policy', # Modern name for Feature-Policy
    'Feature-Policy', # Older name, still sometimes seen
    'Cache-Control',
    'Pragma',
    'Expires',
    'Set-Cookie', # Special handling due to multiple instances and attributes
    'Server', # Informational
    'X-Powered-By', # Informational
    'X-XSS-Protection', # Deprecated by modern browsers, but still seen
    'Access-Control-Allow-Origin' # CORS header
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 BugBountyHunterTool/1.0'

def parse_cookies(cookie_string_list):
    """
    Parses one or more Set-Cookie header strings into a list of dictionaries.
    Note: This is a simplified parser. Full cookie parsing can be complex.
    """
    parsed_cookies = []
    if not cookie_string_list:
        return parsed_cookies

    # If response.headers gives a single string for Set-Cookie (it shouldn't, but to be safe)
    if isinstance(cookie_string_list, str):
        cookie_string_list = [cookie_string_list]

    for cookie_str in cookie_string_list:
        parts = [p.strip() for p in cookie_str.split(';')]
        if not parts:
            continue

        name_value_part = parts[0]
        name_value = name_value_part.split('=', 1)
        cookie_details = {'name': name_value[0], 'value': name_value[1] if len(name_value) > 1 else ''}

        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                cookie_details[key.lower()] = value
            else:
                # Attributes like HttpOnly, Secure
                cookie_details[part.lower()] = True
        parsed_cookies.append(cookie_details)
    return parsed_cookies


def analyze_headers(url):
    """
    Fetches and analyzes HTTP headers for a given URL.

    Args:
        url (str): The URL to analyze.

    Returns:
        dict: A dictionary containing 'all_headers' and 'security_headers_status',
              or None if the request fails.
    """
    headers = {'User-Agent': USER_AGENT}
    result = {
        'all_headers': {},
        'security_headers_status': {}
    }

    try:
        print(f"[*] Fetching headers for: {url}")
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Store all headers
        for header_name, header_value in response.headers.items():
            result['all_headers'][header_name] = header_value

        # Check for specific security headers
        for header_name in SECURITY_HEADERS_TO_CHECK:
            # Use .get() for case-insensitive matching provided by requests.structures.CaseInsensitiveDict
            header_value = response.headers.get(header_name)

            if header_name == 'Set-Cookie': # Check specifically for 'Set-Cookie'
                # Use response.cookies (requests.cookies.RequestsCookieJar) for parsed cookies
                # This handles multiple Set-Cookie headers correctly and parses them.
                # However, the requirement is to show HttpOnly, Secure, SameSite attributes
                # which are part of the Set-Cookie header string, not easily available in response.cookies objects.
                # So, we need to access the raw headers.
                raw_cookies = response.raw.headers.getlist('Set-Cookie') # Gets all Set-Cookie headers as a list
                if raw_cookies: # If there are any Set-Cookie headers
                    result['security_headers_status'][header_name] = parse_cookies(raw_cookies)
                else:
                    result['security_headers_status'][header_name] = "Not Present"
            elif header_value is not None:
                result['security_headers_status'][header_name] = header_value
            else:
                result['security_headers_status'][header_name] = "Not Present"

        return result

    except requests.exceptions.HTTPError as e:
        print(f"[!] HTTP error for {url}: {e.response.status_code} {e.response.reason}")
        if e.response is not None:
            for header_name, header_value in e.response.headers.items():
                result['all_headers'][header_name] = header_value
            for header_name in SECURITY_HEADERS_TO_CHECK:
                header_value = e.response.headers.get(header_name)
                if header_name == 'Set-Cookie':
                     raw_cookies = e.response.raw.headers.getlist('Set-Cookie')
                     result['security_headers_status'][header_name] = parse_cookies(raw_cookies) if raw_cookies else "Not Present"
                elif header_value is not None:
                    result['security_headers_status'][header_name] = header_value
                else:
                    result['security_headers_status'][header_name] = "Not Present"
            return result
        return None
    except requests.exceptions.Timeout:
        print(f"[!] Timeout while connecting to {url}.")
        return None
    except requests.exceptions.ConnectionError:
        print(f"[!] Connection error for {url}. Check URL or network.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching {url}: {e}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP Header Analyzer")
    parser.add_argument("url", help="URL to analyze (e.g., http://example.com)")

    args = parser.parse_args()

    if not args.url.startswith(('http://', 'https://')):
        print("[!] URL must start with http:// or https://")
        sys.exit(1)

    analysis_result = analyze_headers(args.url)

    if analysis_result:
        print("\n\n" + "="*20 + " Full HTTP Headers " + "="*20)
        # Using json.dumps for a nice, readable print of the dictionary
        print(json.dumps(analysis_result['all_headers'], indent=2, sort_keys=True))

        print("\n\n" + "="*20 + " Security Headers Analysis " + "="*20)
        for header_name_to_check in SECURITY_HEADERS_TO_CHECK: # Iterate in defined order
            status = analysis_result['security_headers_status'].get(header_name_to_check, "Not Present (Error in script)")
            if header_name_to_check == 'Set-Cookie' and isinstance(status, list):
                print(f"\n  {header_name_to_check}:")
                if not status:
                     print(f"    Not Present")
                for cookie_detail in status:
                    attrs = [f"{k}={v}" for k, v in cookie_detail.items() if k not in ['name', 'value']]
                    print(f"    - Name  : {cookie_detail.get('name')}")
                    print(f"      Value : {cookie_detail.get('value')}")
                    print(f"      Attrib: {', '.join(attrs) if attrs else 'N/A'}")
            else:
                print(f"  {header_name_to_check}: {status}")
        print("="*60 + "\n")
    else:
        print(f"[*] No analysis results for {args.url}.")
