import json
import os
import sys

# Attempt to import ConfigManager for type hinting, not strictly needed for functionality
try:
    from config_manager import ConfigManager
except ImportError:
    ConfigManager = None # Allows script to be parsed if src path not yet set

class Reporter:
    """
    Handles reporting of scan findings to console and file.
    """
    def __init__(self, config_manager_instance):
        """
        Initializes the Reporter.

        Args:
            config_manager_instance (ConfigManager): An instance of ConfigManager.
                                                    (Currently not used but good for future extensibility).
        """
        if ConfigManager and not isinstance(config_manager_instance, ConfigManager):
            # This check is lenient if ConfigManager couldn't be imported (e.g. during tests)
            # but strict if it was imported.
            if ConfigManager is not None : # Only raise if ConfigManager was successfully imported
                 raise TypeError("config_manager_instance must be an instance of ConfigManager or a compatible mock.")
        self.config = config_manager_instance # Store for future use

    def print_console(self, findings):
        """
        Prints findings to the console in a human-readable format.

        Args:
            findings (list): A list of finding dictionaries.
        """
        if not findings:
            print("\n[*] No findings to report to console.")
            return

        print("\n\n==================== CONSOLE REPORT ====================")
        for i, finding in enumerate(findings):
            type_str = finding.get('type', 'N/A').upper()
            print(f"\n[+] Potential {type_str} Found! (#{i+1})")
            print(f"  URL:       {finding.get('url', 'N/A')}")
            print(f"  Parameter: {finding.get('parameter', 'N/A')}")
            print(f"  Payload:   {str(finding.get('payload', 'N/A'))[:100]}") # Limit payload length in console
            print(f"  Type:      {finding.get('type', 'N/A')}")
            if 'evidence' in finding:
                print(f"  Evidence:  {str(finding.get('evidence', 'N/A'))[:200]}") # Limit evidence length
            if 'response_status' in finding:
                 print(f"  Status:    {finding.get('response_status', 'N/A')}")
            print("----------------------------------------------------")
        print("================ END OF CONSOLE REPORT ================")


    def save_to_file(self, findings, output_filepath):
        """
        Saves findings to a file in JSON Lines format.

        Args:
            findings (list): A list of finding dictionaries.
            output_filepath (str): The path to the output file.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        if not findings:
            print("\n[*] No findings to save to file.")
            return True # Nothing to save is not an error

        print(f"\n[*] Attempting to save {len(findings)} findings to: {output_filepath}")
        try:
            # Ensure directory exists
            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"  [Info] Created directory: {output_dir}")

            with open(output_filepath, 'w') as f:
                for finding in findings:
                    f.write(json.dumps(finding) + '\n')
            print(f"  [+] Findings successfully saved to: {output_filepath}")
            return True
        except IOError as e:
            print(f"  [!] Error: Could not write to file {output_filepath}. {e}")
            return False
        except Exception as e:
            print(f"  [!] Error: An unexpected error occurred while saving to file: {e}")
            return False

if __name__ == '__main__':
    # --- Standalone Testing Setup for Reporter ---
    # This mock allows testing reporter without needing the full ConfigManager
    # if this script is run directly and imports might fail.
    class MockConfigManagerForReporter:
        def get_setting(self, key, default=None):
            # print(f"(MockConfigManager) get_setting called for {key}")
            return default

    # Adjust sys.path to allow finding config_manager if it's in the same directory (src)
    # This is mainly for when this script is run directly as __main__.
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    if current_script_dir not in sys.path:
        sys.path.insert(0, current_script_dir)

    # If ConfigManager was not imported at the top, try again now that path might be set
    if ConfigManager is None:
        try:
            from config_manager import ConfigManager
        except ImportError:
            print("[Reporter Test] Warning: Could not import actual ConfigManager for test, using basic mock.", file=sys.stderr)
            ConfigManager = MockConfigManagerForReporter # Fallback to simpler mock if import still fails

    # Use either the imported ConfigManager or the simple mock
    config_mngr_instance = ConfigManager() if ConfigManager is not MockConfigManagerForReporter else MockConfigManagerForReporter()

    reporter_instance = Reporter(config_mngr_instance)

    sample_findings_data = [
        {
            'url': "http://test.com/vuln.php?id=1%27+OR+%271%27%3D%271", # URL encoded for realism
            'parameter': 'id',
            'payload': "' OR '1'='1",
            'type': 'sqli:error-based',
            'evidence': 'You have an error in your SQL syntax',
            'response_status': 200
        },
        {
            'url': "http://test.com/search?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
            'parameter': 'q',
            'payload': '<script>alert(1)</script>',
            'type': 'xss:reflected',
            'evidence': 'Payload reflected in response body',
            'response_status': 200
        },
        { # Finding with minimal fields
            'url': "http://test.com/page?param=value",
            'parameter': 'param',
            'payload': 'some_payload',
            'type': 'generic-test'
        }
    ]

    print("--- Reporter: Testing Console Output ---")
    reporter_instance.print_console(sample_findings_data)
    reporter_instance.print_console([]) # Test with no findings

    output_test_filename = 'test_report_output.jsonl'
    print(f"\n--- Reporter: Testing File Output (to {output_test_filename}) ---")
    success_save = reporter_instance.save_to_file(sample_findings_data, output_test_filename)

    if success_save and os.path.exists(output_test_filename):
        print(f"\nContent of {output_test_filename}:")
        line_count = 0
        try:
            with open(output_test_filename, 'r') as f_read:
                for line in f_read:
                    print(line, end='') # Print line as is (includes newline)
                    line_count +=1
            if line_count == len(sample_findings_data):
                print(f"\n[+] File content verified: {line_count} lines written successfully.")
            else:
                print(f"\n[!] File content mismatch: Expected {len(sample_findings_data)} lines, got {line_count}.")

        except IOError as e:
            print(f"[!] Error reading back test file: {e}")
        finally:
            os.remove(output_test_filename) # Clean up test file
            print(f"\n[*] Cleaned up {output_test_filename}.")
    elif success_save and not sample_findings_data: # If save was "successful" because no data
        pass
    else:
        print(f"[!] Failed to save or verify file {output_test_filename}.")

    print("\n--- Reporter: Testing File Output with no findings ---")
    reporter_instance.save_to_file([], "empty_report.jsonl") # Should just print "No findings"

    print("\n[*] Reporter Standalone Test Suite Finished.")
