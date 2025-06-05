import yaml
import os
import json # For json.dump in example, though main lib is YAML

class ConfigManager:
    """
    Manages configuration settings for the Advanced Bounty Scanner.
    Loads settings from a YAML file and allows overriding them.
    """
    def __init__(self, default_config_path=None):
        """
        Initializes the ConfigManager.

        Args:
            default_config_path (str, optional): Path to a default YAML configuration file.
        """
        self.settings = {}
        self._load_default_settings()

        if default_config_path:
            self.load_from_file(default_config_path)

    def _load_default_settings(self):
        """
        Loads hardcoded default settings.
        These are overridden by values from a config file or programmatic updates.
        """
        self.settings = {
            'user_agent': 'AdvancedBountyScanner/0.1 (Default)',
            'timeout': 10,  # seconds
            'proxy': None,  # e.g., {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'}
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            },
            'rate_limit': 0,  # requests per second (0 = no limit)
            'max_concurrent_requests': 5,
            'wordlists': { # Default paths for various wordlists, relative to a base 'wordlists' dir
                'subdomains': 'subdomains_default.txt',
                'directories': 'directories_default.txt',
                'passwords': 'passwords_default.txt',
            },
            'output_directory': 'results' # Default directory for saving scan results
        }
        # Ensure internal structure is copied if it's a mutable type like dict
        self.settings['headers'] = self.settings['headers'].copy()
        self.settings['wordlists'] = self.settings['wordlists'].copy()


    def load_from_file(self, file_path):
        """
        Loads configuration from a YAML file, merging with existing settings.

        Args:
            file_path (str): Path to the YAML configuration file.

        Returns:
            bool: True if loading was successful, False otherwise.
        """
        if not os.path.exists(file_path):
            print(f"[ConfigManager] Error: Configuration file not found at {file_path}")
            return False

        try:
            with open(file_path, 'r') as f:
                file_config = yaml.safe_load(f)

            if file_config: # If file is not empty
                # Deep merge file_config into self.settings
                # A simple self.settings.update(file_config) would overwrite nested dicts entirely.
                self._deep_update(self.settings, file_config)
                print(f"[ConfigManager] Configuration loaded successfully from {file_path}")
                return True
            else:
                print(f"[ConfigManager] Warning: Configuration file {file_path} is empty.")
                return True # Technically successful load of an empty file
        except yaml.YAMLError as e:
            print(f"[ConfigManager] Error parsing YAML configuration file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"[ConfigManager] An unexpected error occurred while loading {file_path}: {e}")
            return False

    def _deep_update(self, base_dict, update_dict):
        """Helper function to recursively update a dictionary."""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


    def get_setting(self, key, default_value=None):
        """
        Retrieves a configuration setting.

        Args:
            key (str): The name of the setting (e.g., 'user_agent', 'timeout').
                       For nested settings, use dot notation (e.g., 'wordlists.subdomains').
            default_value (any, optional): Value to return if the key is not found.

        Returns:
            any: The value of the setting, or default_value if not found.
        """
        if '.' in key:
            # Handle nested keys
            keys = key.split('.')
            current_level = self.settings
            for k in keys:
                if isinstance(current_level, dict) and k in current_level:
                    current_level = current_level[k]
                else:
                    return default_value
            return current_level
        return self.settings.get(key, default_value)

    def update_setting(self, key, value):
        """
        Updates or adds a single configuration setting.

        Args:
            key (str): The name of the setting. For nested settings, use dot notation.
            value (any): The new value for the setting.
        """
        if '.' in key:
            keys = key.split('.')
            current_level = self.settings
            for i, k in enumerate(keys[:-1]): # Iterate until the second to last key
                if k not in current_level or not isinstance(current_level[k], dict):
                    current_level[k] = {} # Create a dict if path doesn't exist
                current_level = current_level[k]
            current_level[keys[-1]] = value
        else:
            self.settings[key] = value
        # print(f"[ConfigManager] Setting '{key}' updated.") # Optional: for verbosity

    def override_config(self, config_dict):
        """
        Overrides multiple settings using a dictionary.
        Performs a deep update.

        Args:
            config_dict (dict): A dictionary of settings to update. The keys in this dictionary
                                will overwrite the corresponding top-level keys in the current settings.
                                If a key in config_dict points to a nested dictionary, that entire
                                nested structure will replace the one in the current settings for that key.
        """
        if isinstance(config_dict, dict):
            # Perform a direct update for top-level keys.
            # This means if a key in config_dict is also a dict, it replaces the existing dict for that key.
            self.settings.update(config_dict)
            # print("[ConfigManager] Configuration overridden with provided dictionary.") # Optional
        else:
            print("[ConfigManager] Error: override_config expects a dictionary.")


if __name__ == '__main__':
    print("[*] ConfigManager Test Suite")

    # --- Test Setup: Create a dummy config file ---
    dummy_config_data = {
        'user_agent': 'TestAgent/1.0 from File',
        'timeout': 15,
        'proxy': {'http': 'http://fileproxy:8080', 'https': 'http://fileproxy:8080'},
        'headers': { # Overrides 'Accept', adds 'X-Custom-Header'
            'Accept': 'application/json',
            'X-Custom-Header': 'FileValue'
        },
        'custom_setting_from_file': 'hello_world',
        'wordlists': { # Overrides 'subdomains', adds 'lfi'
            'subdomains': 'subdomains_from_file.txt',
            'lfi': 'lfi_paths.txt'
        }
    }
    temp_config_file_path = 'temp_config_test.yaml'
    with open(temp_config_file_path, 'w') as f:
        yaml.dump(dummy_config_data, f)

    # --- Test 1: Initialization with Defaults ---
    print("\n--- Test 1: Defaults ---")
    cm_default = ConfigManager()
    print(f"Default User-Agent: {cm_default.get_setting('user_agent')}")
    print(f"Default Timeout: {cm_default.get_setting('timeout')}")
    print(f"Default Proxy: {cm_default.get_setting('proxy')}") # Should be None
    print(f"Default Max Concurrent: {cm_default.get_setting('max_concurrent_requests')}")
    print(f"Default Header 'Accept': {cm_default.get_setting('headers.Accept')}")
    print(f"Default Wordlist for Subdomains: {cm_default.get_setting('wordlists.subdomains')}")

    # --- Test 2: Loading from file (implicitly in constructor) ---
    print("\n--- Test 2: Load from file (on init) ---")
    cm_file_init = ConfigManager(default_config_path=temp_config_file_path)
    print(f"File User-Agent (init): {cm_file_init.get_setting('user_agent')}") # Overridden
    print(f"File Timeout (init): {cm_file_init.get_setting('timeout')}") # Overridden
    print(f"File Proxy (init): {cm_file_init.get_setting('proxy')}") # Overridden
    print(f"File Custom Setting (init): {cm_file_init.get_setting('custom_setting_from_file')}") # New
    print(f"File Header 'Accept' (init): {cm_file_init.get_setting('headers.Accept')}") # Overridden
    print(f"File Header 'Accept-Language' (init): {cm_file_init.get_setting('headers.Accept-Language')}") # Default, preserved
    print(f"File Header 'X-Custom-Header' (init): {cm_file_init.get_setting('headers.X-Custom-Header')}") # New from file
    print(f"File Wordlist for Subdomains (init): {cm_file_init.get_setting('wordlists.subdomains')}") # Overridden
    print(f"File Wordlist for LFI (init): {cm_file_init.get_setting('wordlists.lfi')}") # New from file
    print(f"Default Wordlist for Directories (init): {cm_file_init.get_setting('wordlists.directories')}") # Default, preserved

    # --- Test 3: Loading from file (explicitly) ---
    print("\n--- Test 3: Load from file (explicitly) ---")
    cm_file_explicit = ConfigManager() # Start with defaults
    cm_file_explicit.load_from_file(temp_config_file_path)
    print(f"File User-Agent (explicit): {cm_file_explicit.get_setting('user_agent')}")
    print(f"File Timeout (explicit): {cm_file_explicit.get_setting('timeout')}")
    print(f"File Custom Setting (explicit): {cm_file_explicit.get_setting('custom_setting_from_file')}")

    # --- Test 4: Update/Override individual settings ---
    print("\n--- Test 4: Update/Override Settings ---")
    cm_override = ConfigManager(default_config_path=temp_config_file_path) # Loaded from file
    cm_override.update_setting('timeout', 25) # Override timeout
    cm_override.update_setting('new_runtime_setting', True) # Add new setting
    cm_override.update_setting('proxy.http', 'http://runtimeproxy:1234') # Update nested
    cm_override.update_setting('headers.X-Runtime-Header', 'AddedAtRuntime') # Add nested header
    print(f"Overridden Timeout: {cm_override.get_setting('timeout')}")
    print(f"Runtime New Setting: {cm_override.get_setting('new_runtime_setting')}")
    print(f"Overridden Proxy HTTP: {cm_override.get_setting('proxy.http')}")
    print(f"Original Proxy HTTPS: {cm_override.get_setting('proxy.https')}") # Should be from file
    print(f"Runtime Header 'X-Runtime-Header': {cm_override.get_setting('headers.X-Runtime-Header')}")
    print(f"File Header 'X-Custom-Header' (preserved): {cm_override.get_setting('headers.X-Custom-Header')}")


    # --- Test 5: Override_config with a dictionary ---
    print("\n--- Test 5: Override_config with dictionary ---")
    cm_dict_override = ConfigManager(default_config_path=temp_config_file_path)
    override_data = {
        'timeout': 30,
        'rate_limit': 10,
        'proxy': {'https': 'https://newruntimeproxy:4321'}, # Overwrites entire proxy dict
        'headers': {'X-Another-Runtime': 'FromDict'}, # Overwrites entire headers dict from file
        'wordlists': {'subdomains': 'overridden_subs.txt'} # Overwrites entire wordlists dict from file
    }
    cm_dict_override.override_config(override_data)
    print(f"Dict Override Timeout: {cm_dict_override.get_setting('timeout')}")
    print(f"Dict Override Rate Limit: {cm_dict_override.get_setting('rate_limit')}")
    print(f"Dict Override Proxy HTTP (should be None now): {cm_dict_override.get_setting('proxy.http')}")
    print(f"Dict Override Proxy HTTPS: {cm_dict_override.get_setting('proxy.https')}")
    print(f"Dict Override Header 'X-Another-Runtime': {cm_dict_override.get_setting('headers.X-Another-Runtime')}")
    print(f"Dict Override Header 'Accept' (should be None now): {cm_dict_override.get_setting('headers.Accept')}")
    print(f"Dict Override Wordlist Subdomains: {cm_dict_override.get_setting('wordlists.subdomains')}")
    print(f"Dict Override Wordlist LFI (should be None now): {cm_dict_override.get_setting('wordlists.lfi')}")


    # --- Test 6: Get non-existent setting ---
    print("\n--- Test 6: Get Non-Existent Setting ---")
    print(f"Non-existent (no default): {cm_override.get_setting('does_not_exist')}") # Expect None
    print(f"Non-existent (with fallback): {cm_override.get_setting('does_not_exist_either', 'fallback_value_here')}")
    print(f"Non-existent nested (no default): {cm_override.get_setting('proxy.ftp.url')}")


    # --- Test 7: Load non-existent file ---
    print("\n--- Test 7: Load Non-Existent File ---")
    cm_non_existent_file = ConfigManager()
    success = cm_non_existent_file.load_from_file('non_existent_config.yaml')
    print(f"Load success for non_existent_config.yaml: {success}") # Expect False
    print(f"User-Agent after trying to load non-existent file: {cm_non_existent_file.get_setting('user_agent')}") # Should be default


    # --- Test 8: Load empty YAML file ---
    print("\n--- Test 8: Load Empty YAML file ---")
    empty_yaml_path = "empty_test_config.yaml"
    with open(empty_yaml_path, 'w') as f:
        f.write("") # Create empty file
    cm_empty_file = ConfigManager()
    success_empty = cm_empty_file.load_from_file(empty_yaml_path)
    print(f"Load success for {empty_yaml_path}: {success_empty}") # Expect True
    print(f"User-Agent after loading empty file: {cm_empty_file.get_setting('user_agent')}") # Should be default
    os.remove(empty_yaml_path)


    # --- Test 9: Load malformed YAML file ---
    print("\n--- Test 9: Load Malformed YAML file ---")
    malformed_yaml_path = "malformed_test_config.yaml"
    with open(malformed_yaml_path, 'w') as f:
        f.write("user_agent: Test\n  bad_indent: Problem") # Malformed YAML
    cm_malformed_file = ConfigManager()
    success_malformed = cm_malformed_file.load_from_file(malformed_yaml_path)
    print(f"Load success for {malformed_yaml_path}: {success_malformed}") # Expect False
    print(f"User-Agent after loading malformed file: {cm_malformed_file.get_setting('user_agent')}") # Should be default
    os.remove(malformed_yaml_path)

    # --- Clean up dummy config file ---
    if os.path.exists(temp_config_file_path):
        os.remove(temp_config_file_path)

    print("\n[*] ConfigManager Test Suite Finished.")
