"""
Generate a CSV template from a text list of emails or names+emails.

Usage:
    python3 outreach/generate_csv.py "email1@example.com, email2@example.com"
    python3 outreach/generate_csv.py --file contacts.txt

Contact file format (one per line):
    John Doe <john@example.com>
    or just: john@example.com
"""

import csv
import os
import sys
import re

OUTPUT = os.path.join(os.path.dirname(__file__), "contacts.csv")


def parse_line(line):
    line = line.strip()
    if not line:
        return None
    # Try "Name <email>" format
    m = re.match(r'([^<]+)\s*<([^>]+)>', line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # Try "name,email" CSV format
    if ',' in line:
        parts = line.split(',', 1)
        return parts[0].strip(), parts[1].strip()
    # Assume just email
    return line.split('@')[0], line


def main():
    contacts = []
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        with open(sys.argv[2]) as f:
            for line in f:
                parsed = parse_line(line)
                if parsed:
                    contacts.append(parsed)
    elif len(sys.argv) >= 2:
        raw = sys.argv[1]
        for item in raw.split(","):
            parsed = parse_line(item)
            if parsed:
                contacts.append(parsed)
    else:
        # Interactive mode
        print("Paste contacts (one per line). Press Ctrl+D when done:")
        for line in sys.stdin:
            parsed = parse_line(line)
            if parsed:
                contacts.append(parsed)

    if not contacts:
        print("No contacts found.")
        sys.exit(1)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email"])
        for name, email in contacts:
            writer.writerow([name, email])

    print(f"✅ Wrote {len(contacts)} contacts to {OUTPUT}")
    print(f"   Then run: python3 outreach/send_invites.py {OUTPUT}")


if __name__ == "__main__":
    main()
