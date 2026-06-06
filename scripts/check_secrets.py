import sys
import os
import re

# Same patterns as in utils.py
PATTERNS = [
    r"(sk-[a-zA-Z0-9]{32,})", # OpenAI/Anthropic
    r"(AIza[0-9A-Za-z-_]{35})", # Google
]

def scan_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        for pattern in PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                return True, matches
    return False, []

def main():
    found_secrets = False
    files_to_check = sys.argv[1:]

    for file_path in files_to_check:
        if os.path.isdir(file_path):
            continue

        has_secret, matches = scan_file(file_path)
        if has_secret:
            print(f"❌ ERROR: Potential API key found in {file_path}")
            for m in matches:
                # Print masked version for security
                masked = m[:6] + "..." + m[-4:]
                print(f"   - Match: {masked}")
            found_secrets = True

    if found_secrets:
        print("\n🚫 Commit blocked. Please remove the secrets or use an environment variable.")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
