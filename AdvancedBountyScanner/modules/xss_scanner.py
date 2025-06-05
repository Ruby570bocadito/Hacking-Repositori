import sys
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Attempt to import CoreEngine and ConfigManager for type hinting
try:
    from core_engine import CoreEngine
    from config_manager import ConfigManager
except ImportError:
    CoreEngine = None
    ConfigManager = None


class XSSScanner:
    """
    Scans URLs for basic reflected XSS vulnerabilities in GET parameters.
    """

    # Payloads designed to be reflected. Using a unique marker for easier detection.
    # Some payloads are standard, others use a specific marker.
    UNIQUE_MARKER = "JULES_XSS_TEST_STRING_12345"
    XSS_PAYLOADS = [
        f"<ScRipT>alert('{UNIQUE_MARKER}_SCRIPT')</ScRipT>",
        f"'\"><img src=x onerror=alert('{UNIQUE_MARKER}_IMG')>",
        f"';alert('{UNIQUE_MARKER}_JS');'",
        f"</title><script>alert('{UNIQUE_MARKER}_TITLE')</script>",
        f"{UNIQUE_MARKER}",
        # Some very simple, common patterns
        "<h1>test</h1>",
        "<plaintext>"
    ]

    def __init__(self, core_engine_instance, config_manager_instance):
        """
        Initializes the XSSScanner.

        Args:
            core_engine_instance (CoreEngine): An instance of the CoreEngine.
            config_manager_instance (ConfigManager): An instance of the ConfigManager.
        """
        if CoreEngine is None or ConfigManager is None:
            raise ImportError("CoreEngine or ConfigManager not imported. Ensure 'src' is in sys.path.")

        if not isinstance(core_engine_instance, CoreEngine):
            raise TypeError("core_engine_instance must be an instance of CoreEngine")
        if not isinstance(config_manager_instance, ConfigManager):
            raise TypeError("config_manager_instance must be an instance of ConfigManager")

        self.engine = core_engine_instance
        self.config = config_manager_instance
        self.user_agent = self.config.get_setting('user_agent', 'AdvancedBountyScanner/0.1 (XSSModule)')
        self.timeout = self.config.get_setting('timeout', 10)

    def scan_url(self, target_url):
        """
        Scans a given URL for reflected XSS vulnerabilities in its GET parameters.

        Args:
            target_url (str): The URL to scan.

        Returns:
            list: A list of dictionaries, where each dictionary represents a potential finding.
                  Returns an empty list if no vulnerabilities are found or if the URL has no parameters.
        """
        potential_findings = []
        parsed_url = urlparse(target_url)
        original_query_params = parse_qs(parsed_url.query, keep_blank_values=True)

        if not original_query_params:
            # print(f"[*] No GET parameters found in {target_url}. Skipping XSS parameter scan.")
            return potential_findings

        print(f"[*] Scanning URL for XSS: {target_url}")

        for param_name, param_values in original_query_params.items():
            original_value = param_values[0] if param_values else ""

            for payload in self.XSS_PAYLOADS:
                test_params = {k: v[:] for k, v in original_query_params.items()}

                # Inject payload (URL encoding will be handled by urlencode)
                test_params[param_name] = [payload] # Simple replacement for this test case
                                                    # More advanced might try original_value + payload

                new_query_string = urlencode(test_params, doseq=True)
                test_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query_string, parsed_url.fragment))

                # print(f"  [Testing XSS] {param_name} with payload: {payload[:30]}... -> {test_url}") # Verbose

                response = self.engine.make_request(
                    test_url,
                    method='GET',
                    headers={'User-Agent': self.user_agent},
                    timeout=self.timeout,
                    allow_redirects=False # Important to see direct reflection
                )

                if response and response.text:
                    # Check if the exact payload (or its unique marker part) is reflected
                    # This is a simple check for reflected XSS. Real XSS can be more complex.
                    search_term = self.UNIQUE_MARKER if self.UNIQUE_MARKER in payload else payload

                    if search_term in response.text:
                        finding = {
                            'url': test_url,
                            'parameter': param_name,
                            'payload': payload,
                            'type': 'reflected-xss',
                            'evidence': f"Payload found in response. Search term: '{search_term}'",
                            'response_status': response.status_code
                        }
                        potential_findings.append(finding)
                        print(f"  [+] Potential XSS: Param='{param_name}', Payload='{payload[:50]}...', Evidence='{finding['evidence']}'")
                        # No break here, a parameter might be vulnerable to multiple payloads / reflections

        return potential_findings


if __name__ == '__main__':
    # --- Standalone Testing Setup ---
    current_module_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_module_dir)
    src_dir_path = os.path.join(project_root_dir, 'src')
    if src_dir_path not in sys.path:
        sys.path.insert(0, src_dir_path)

    try:
        from core_engine import CoreEngine
        from config_manager import ConfigManager
    except ImportError as e:
        print(f"[ERROR] Failed to import CoreEngine or ConfigManager for testing: {e}")
        sys.exit(1)

    class MockXSSCoreEngine(CoreEngine):
        """A mock CoreEngine for testing the XSSScanner."""
        def make_request(self, url, method='GET', headers=None, params=None, data=None, json_payload=None, allow_redirects=True, **kwargs):
            print(f"  [Mock Engine] Requesting: {method} {url}")
            parsed_url_for_mock = urlparse(url)
            query_params_for_mock = parse_qs(parsed_url_for_mock.query)

            response_text_content = "<html><body>Standard page content.</body></html>"

            # Simulate reflection for 'query' parameter
            if 'query' in query_params_for_mock:
                query_val = query_params_for_mock['query'][0] # Get the first value
                # Check if any of our XSS payloads (or their markers) are in the query_val
                if XSSScanner.UNIQUE_MARKER in query_val or "<ScRipT>" in query_val or "<h1>test</h1>" in query_val:
                    response_text_content = f"<html><body>Search results for: {query_val}</body></html>"
                    print(f"  [Mock Engine] Simulated XSS reflection for query parameter with value: {query_val[:60]}...")

            # Simulate reflection for 'name' parameter with a specific payload
            if 'name' in query_params_for_mock:
                name_val = query_params_for_mock['name'][0]
                if XSSScanner.UNIQUE_MARKER in name_val:
                     response_text_content = f"<html><head><title>User: {name_val}</title></head><body>Hello, {name_val}!</body></html>"
                     print(f"  [Mock Engine] Simulated XSS reflection for name parameter with value: {name_val[:60]}...")


            class MockResponse:
                def __init__(self, text_val, status_code_val=200, ok_val=True):
                    self.text = text_val
                    self.content = text_val.encode('utf-8')
                    self.status_code = status_code_val
                    self.ok = ok_val
                    self.headers = {'Content-Type': 'text/html'}

            return MockResponse(response_text_content)

    print("[*] XSSScanner Standalone Test Suite")

    test_config_manager = ConfigManager()
    test_core_engine_mock = MockXSSCoreEngine(
        default_headers=test_config_manager.get_setting('headers'),
        timeout=test_config_manager.get_setting('timeout')
    )
    xss_scanner_instance = XSSScanner(test_core_engine_mock, test_config_manager)

    print("\n--- Testing XSS Scanner with a mock vulnerable URL (param 'query') ---")
    test_url_vulnerable_query = "http://testserver.com/search?query=initial_value&page=1"
    print(f"[*] Scanning vulnerable URL (param 'query'): {test_url_vulnerable_query}")
    findings_vulnerable_q = xss_scanner_instance.scan_url(test_url_vulnerable_query)

    if findings_vulnerable_q:
        print("\n[+] XSS Findings (Mock Vulnerable URL - 'query' param):")
        for finding in findings_vulnerable_q:
            print(f"  URL: {finding['url']}")
            print(f"  Param: {finding['parameter']}")
            print(f"  Payload: {finding['payload'][:60]}...") # Truncate long payloads
            print(f"  Type: {finding['type']}")
            print(f"  Evidence: {finding['evidence']}\n")
    else:
        print("\n[-] No XSS findings for 'query' param. This might indicate an issue in test setup or scan logic.")

    print("\n--- Testing XSS Scanner with a mock vulnerable URL (param 'name') ---")
    test_url_vulnerable_name = "http://testserver.com/profile.php?id=10&name=guest"
    print(f"[*] Scanning vulnerable URL (param 'name'): {test_url_vulnerable_name}")
    findings_vulnerable_n = xss_scanner_instance.scan_url(test_url_vulnerable_name)

    if findings_vulnerable_n:
        print("\n[+] XSS Findings (Mock Vulnerable URL - 'name' param):")
        for finding in findings_vulnerable_n:
            print(f"  URL: {finding['url']}")
            print(f"  Param: {finding['parameter']}")
            print(f"  Payload: {finding['payload'][:60]}...")
            print(f"  Type: {finding['type']}")
            print(f"  Evidence: {finding['evidence']}\n")
    else:
        print("\n[-] No XSS findings for 'name' param. This might indicate an issue in test setup or scan logic.")


    print("\n--- Testing XSS Scanner with a mock non-vulnerable URL ---")
    test_url_non_vulnerable = "http://testserver.com/search?safe_query=data&page=2"
    print(f"[*] Scanning non-vulnerable URL: {test_url_non_vulnerable}")
    findings_non_vuln = xss_scanner_instance.scan_url(test_url_non_vulnerable)
    if not findings_non_vuln:
        print("\n[-] Scan on non-vulnerable URL correctly yielded no findings.")
    else:
        print("\n[!] Scan on non-vulnerable URL yielded findings, check mock or logic:")
        for finding in findings_non_vuln: print(f"  - {finding}")


    print("\n--- Testing XSS Scanner with a URL with no parameters ---")
    test_url_no_params = "http://testserver.com/index.html"
    print(f"[*] Scanning URL with no params: {test_url_no_params}")
    findings_no_params = xss_scanner_instance.scan_url(test_url_no_params)
    if not findings_no_params:
        print("\n[-] Scan on URL with no params correctly yielded no findings.")
    else:
        print("\n[!] Scan on URL with no params yielded findings, check logic:")
        for finding in findings_no_params: print(f"  - {finding}")

    print("\n[*] XSSScanner Standalone Test Suite Finished.")
