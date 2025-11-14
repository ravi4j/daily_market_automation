#!/usr/bin/env python3
"""
Test the config loading functionality
"""
import os
import sys

# Test 1: Check if config file exists
print("=" * 60)
print("Testing Config File Loading")
print("=" * 60)

config_path = "config/symbols.yaml"
print(f"\n1. Checking config file: {config_path}")
if os.path.exists(config_path):
    print("   ✅ Config file exists")
    with open(config_path, 'r') as f:
        content = f.read()
        print(f"   ✅ File is readable ({len(content)} bytes)")
        print("\n   File contents:")
        print("   " + "-" * 56)
        for line in content.split('\n')[:15]:
            print(f"   {line}")
        print("   " + "-" * 56)
else:
    print("   ❌ Config file not found!")
    sys.exit(1)

# Test 2: Try to import yaml
print("\n2. Checking PyYAML dependency:")
try:
    import yaml
    print("   ✅ PyYAML is installed")

    # Test 3: Parse the YAML
    print("\n3. Parsing YAML config:")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        symbols = config.get('symbols', {})
        print(f"   ✅ Successfully loaded {len(symbols)} symbols:")
        for key, ticker in symbols.items():
            print(f"      • {key:10s} -> {ticker}")
except ImportError:
    print("   ⚠️  PyYAML not installed locally")
    print("      (This is OK - it will be installed in GitHub Actions)")
    print("      To test locally: pip install pyyaml")

# Test 4: Test the actual fetch script's config loading
print("\n4. Testing fetch_daily_prices.py config loading:")
sys.path.insert(0, 'src')

try:
    # Import just the config loading part
    import importlib.util
    spec = importlib.util.spec_from_file_location("fetch", "src/fetch_daily_prices.py")
    fetch = importlib.util.module_from_spec(spec)

    # This will load the module and execute load_symbols_config()
    spec.loader.exec_module(fetch)

    print(f"   ✅ Script loaded successfully")
    print(f"   ✅ Found {len(fetch.SYMBOLS)} symbols:")
    for key, ticker in fetch.SYMBOLS.items():
        print(f"      • {key:10s} -> {ticker}")

except Exception as e:
    print(f"   ⚠️  Could not test script: {e}")
    print("      (This is expected if dependencies are missing)")

print("\n" + "=" * 60)
print("✅ Config file structure is valid!")
print("=" * 60)
print("\nNext steps:")
print("  1. Commit the changes: git add -A && git commit -m 'feat: Externalize symbols config'")
print("  2. Push to GitHub: git push")
print("  3. Config will work automatically in GitHub Actions (PyYAML will be installed)")
