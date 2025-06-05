import requests
import json # For example usage

class CoreEngine:
    """
    Core engine for making HTTP requests with persistent sessions and default configurations.
    """
    def __init__(self, default_headers=None, proxy=None, timeout=10):
        """
        Initializes the CoreEngine.

        Args:
            default_headers (dict, optional): Default headers to be sent with every request.
            proxy (dict, optional): Proxy configuration (e.g., {'http': '...', 'https': '...'}).
            timeout (int, optional): Default timeout in seconds for requests.
        """
        self.session = requests.Session()
        self.default_headers = default_headers if default_headers else {}
        self.proxies = proxy # requests uses 'proxies' argument
        self.timeout = timeout

        # Apply default headers to the session
        if self.default_headers:
            self.session.headers.update(self.default_headers)

        # Apply proxy to the session
        if self.proxies:
            self.session.proxies.update(self.proxies)

    def make_request(self, url, method='GET', headers=None, params=None, data=None, json_payload=None, allow_redirects=True, **kwargs):
        """
        Makes an HTTP request.

        Args:
            url (str): The URL for the request.
            method (str, optional): HTTP method (GET, POST, PUT, DELETE, etc.). Defaults to 'GET'.
            headers (dict, optional): Headers to merge with default headers for this request.
            params (dict, optional): URL parameters for GET requests.
            data (dict or bytes, optional): Data to send in the body (form-encoded for dicts).
            json_payload (dict, optional): JSON data to send in the body. 'data' will be ignored if this is set.
            allow_redirects (bool, optional): Whether to follow redirects. Defaults to True.
            **kwargs: Other keyword arguments supported by requests.request (e.g., files, auth).

        Returns:
            requests.Response: The Response object if the request is successful.
            None: If a request exception occurs.
        """
        # Prepare headers: start with session defaults, then update with method-specific defaults, then request-specific
        request_headers = self.session.headers.copy() # Start with session's base headers
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json_payload, # requests uses 'json' argument for json_payload
                timeout=kwargs.pop('timeout', self.timeout), # Use request-specific timeout or default
                proxies=kwargs.pop('proxies', self.session.proxies), # Use request-specific proxies or default
                allow_redirects=allow_redirects,
                **kwargs
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.HTTPError as e:
            # This is for 4xx/5xx responses. We still return the response object
            # as it might contain useful information (e.g. error messages in JSON).
            print(f"[CoreEngine] HTTP Error for {method} {url}: {e}")
            return e.response
        except requests.exceptions.Timeout:
            print(f"[CoreEngine] Timeout for {method} {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[CoreEngine] Connection error for {method} {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[CoreEngine] Request exception for {method} {url}: {e}")
            return None
        except Exception as e:
            print(f"[CoreEngine] An unexpected error occurred for {method} {url}: {e}")
            return None

    def is_successful_response(self, response, success_codes=None):
        """
        Checks if a response indicates success.

        Args:
            response (requests.Response): The response object.
            success_codes (list, optional): List of status codes to consider successful.
                                           Defaults to [200, 201, 202, 204].

        Returns:
            bool: True if the response status code is in the success_codes list, False otherwise.
        """
        if not response:
            return False
        if success_codes is None:
            success_codes = [200, 201, 202, 204] # Common success codes
        return response.status_code in success_codes

    def get_header(self, response, header_name):
        """
        Extracts a specific header from a response.

        Args:
            response (requests.Response): The response object.
            header_name (str): The name of the header to extract.

        Returns:
            str or None: The header value if present, None otherwise.
        """
        if not response or not hasattr(response, 'headers'):
            return None
        return response.headers.get(header_name)


if __name__ == '__main__':
    print("[*] CoreEngine Test Suite")

    # Initialize engine with default User-Agent
    engine = CoreEngine(
        default_headers={'User-Agent': 'AdvancedBountyScanner/0.1 Test Suite'},
        timeout=5 # Quick timeout for tests
    )

    # Test 1: GET request to httpbin
    print("\n[*] Test 1: GET request to httpbin.org/get")
    get_response = engine.make_request('https://httpbin.org/get')
    if get_response:
        print(f"  Status Code: {get_response.status_code}")
        if engine.is_successful_response(get_response):
            print("  GET Response JSON:", json.dumps(get_response.json(), indent=2))
            print(f"  Server Header: {engine.get_header(get_response, 'Server')}")
        else:
            print(f"  GET request failed or returned non-2xx: {get_response.status_code}")
    else:
        print("  GET request to httpbin.org/get failed completely.")

    # Test 2: POST request to httpbin
    print("\n[*] Test 2: POST request to httpbin.org/post")
    post_data = {'name': 'test_user', 'action': 'submit'}
    post_response = engine.make_request('https://httpbin.org/post', method='POST', data=post_data)
    if post_response:
        print(f"  Status Code: {post_response.status_code}")
        if engine.is_successful_response(post_response):
            print("  POST Response JSON:", json.dumps(post_response.json(), indent=2))
        else:
            print(f"  POST request failed or returned non-2xx: {post_response.status_code}")
    else:
        print("  POST request to httpbin.org/post failed completely.")

    # Test 3: JSON POST request to httpbin
    print("\n[*] Test 3: JSON POST request to httpbin.org/post")
    json_payload = {'message': 'hello world', 'id': 123}
    json_post_response = engine.make_request('https://httpbin.org/post', method='POST', json_payload=json_payload)
    if json_post_response:
        print(f"  Status Code: {json_post_response.status_code}")
        if engine.is_successful_response(json_post_response):
            print("  JSON POST Response JSON:", json.dumps(json_post_response.json(), indent=2))
    else:
        print("  JSON POST request to httpbin.org/post failed completely.")

    # Test 4: Request to a non-existent domain
    print("\n[*] Test 4: Request to a non-existent domain")
    error_response = engine.make_request('http://nonexistentdomain123abcxyz.com')
    if not error_response:
        print("  Request to nonexistentdomain123abcxyz.com failed as expected (returned None).")
    elif error_response: # Could be an error response object in some cases (like DNS redirecting to a parking page that gives 404)
        print(f"  Request to nonexistentdomain123abcxyz.com returned response with status: {error_response.status_code}")
        print("  This might happen if DNS resolves to a parking page or similar.")


    # Test 5: Request resulting in HTTP error (e.g., 404)
    print("\n[*] Test 5: Request to a URL that returns 404")
    http_error_response = engine.make_request('https://httpbin.org/status/404')
    if http_error_response: # make_request returns the response object for HTTPError
        print(f"  Status Code: {http_error_response.status_code}")
        if not engine.is_successful_response(http_error_response):
            print("  Received non-2xx status code (e.g., 404) as expected.")
            print(f"  Content (first 100 chars): {http_error_response.text[:100] if http_error_response.text else 'No content'}")
        else:
            print(f"  Received an unexpected successful status code: {http_error_response.status_code}")
    else: # This case should ideally not be hit if the server is reachable and returns 404
        print("  Request to httpbin.org/status/404 failed entirely (returned None), check network or httpbin status.")

    # Test 6: Custom headers for a single request
    print("\n[*] Test 6: GET request with custom headers")
    custom_headers = {'X-Custom-Test': 'HelloWorld123'}
    get_custom_header_response = engine.make_request('https://httpbin.org/headers', headers=custom_headers)
    if get_custom_header_response and engine.is_successful_response(get_custom_header_response):
        response_data = get_custom_header_response.json()
        print(f"  Response Headers JSON: {json.dumps(response_data, indent=2)}")
        if response_data['headers'].get('X-Custom-Test') == 'HelloWorld123' and \
           response_data['headers'].get('User-Agent') == 'AdvancedBountyScanner/0.1 Test Suite':
            print("  Custom header and default User-Agent correctly sent.")
        else:
            print("  Header check failed. Default or custom headers not sent as expected.")
    else:
        print("  GET request with custom headers failed.")

    print("\n[*] CoreEngine Test Suite Finished.")
