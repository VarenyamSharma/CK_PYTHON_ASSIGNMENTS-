import re


# ──────────────────────────────────────────────
#  IPv4 Validator
# ──────────────────────────────────────────────

def validate_ipv4(ip: str) -> tuple[bool, str]:
    """
    Validate a public IPv4 address.

    Rules checked (in order):
      1. Must not be empty.
      2. Must contain exactly 3 dots (4 octets).
      3. Each octet must be a pure integer (no leading zeros,
         no letters, no special characters).
      4. Each octet must be in the range 0–255.
      5. Must NOT be a private / reserved range:
           10.0.0.0/8   · 172.16.0.0/12  · 192.168.0.0/16
           127.0.0.0/8  · 0.0.0.0/8      · 255.255.255.255
    """
    ip = ip.strip()

    if not ip:
        return False, "Error: IP address cannot be empty."

    parts = ip.split(".")

    # Must have exactly 4 parts
    if len(parts) != 4:
        return False, (
            f"Error: Invalid IPv4 format — expected 4 octets separated by dots, "
            f"got {len(parts)}."
        )

    octets = []
    for index, part in enumerate(parts, start=1):
        # Must not be blank
        if not part:
            return False, f"Error: Octet {index} is empty."

        # Must be purely digits
        if not part.isdigit():
            return False, (
                f"Error: Octet {index} ('{part}') contains non-numeric characters."
            )

        # No leading zeros (e.g. "01", "001")
        if len(part) > 1 and part[0] == "0":
            return False, (
                f"Error: Octet {index} ('{part}') has an invalid leading zero."
            )

        value = int(part)
        if value < 0 or value > 255:
            return False, (
                f"Error: Octet {index} ({value}) is out of range — "
                f"each octet must be between 0 and 255."
            )

        octets.append(value)

    a, b, c, d = octets

    # Private / reserved range checks
    if a == 10:
        return False, "Error: '10.x.x.x' is a private IP address, not a public one."
    if a == 172 and 16 <= b <= 31:
        return False, "Error: '172.16.x.x – 172.31.x.x' is a private IP range."
    if a == 192 and b == 168:
        return False, "Error: '192.168.x.x' is a private IP address."
    if a == 127:
        return False, "Error: '127.x.x.x' is the loopback range, not a public address."
    if a == 0:
        return False, "Error: '0.x.x.x' is a reserved address, not a public one."
    if (a, b, c, d) == (255, 255, 255, 255):
        return False, "Error: '255.255.255.255' is the broadcast address."

    return True, f"'{ip}' is a valid public IPv4 address."


# ──────────────────────────────────────────────
#  Gmail Validator
# ──────────────────────────────────────────────

# Permitted special characters in a Gmail username: . _ + -
# (Google silently ignores dots, but they are syntactically allowed.)
GMAIL_USERNAME_RE = re.compile(r'^[a-z0-9][a-z0-9._+\-]*[a-z0-9]$|^[a-z0-9]$')


def validate_gmail(email: str) -> tuple[bool, str]:
    """
    Validate a Gmail address.

    Rules checked (in order):
      1. Must not be empty.
      2. Must end with '@gmail.com' (case-sensitive after normalisation).
      3. There must be exactly one '@'.
      4. Username must be at least 1 character long (Google requires 6,
         but we keep 1 as the hard minimum so the rule is explicitly shown).
      5. Username may only contain: a-z, 0-9, and the symbols . _ + -
      6. Username must start and end with a letter or digit (no leading /
         trailing dots, hyphens, etc.).
      7. Username must not contain consecutive dots (..).
    """
    email = email.strip()

    if not email:
        return False, "Error: Email address cannot be empty."

    # Case-insensitive domain check
    if not email.lower().endswith("@gmail.com"):
        return False, (
            "Error: Not a Gmail address — the address must end with '@gmail.com'."
        )

    # Exactly one '@'
    if email.count("@") != 1:
        return False, "Error: Email must contain exactly one '@' character."

    username = email[: email.index("@")]

    if not username:
        return False, "Error: The username part before '@gmail.com' cannot be empty."

    if len(username) < 6:
        return False, (
            f"Error: Username '{username}' is too short — "
            f"Gmail usernames must be at least 6 characters."
        )

    # Allowed characters
    invalid_chars = set(username) - set("abcdefghijklmnopqrstuvwxyz0123456789._+-")
    if invalid_chars:
        bad = ", ".join(sorted(f"'{c}'" for c in invalid_chars))
        return False, (
            f"Error: Username '{username}' contains invalid character(s): {bad}. "
            f"Only lowercase letters (a-z), digits (0-9), and the symbols . _ + - "
            f"are permitted."
        )

    # Must not start or end with a special character
    if username[0] in "._+-":
        return False, (
            f"Error: Username '{username}' must start with a letter or digit, "
            f"not '{username[0]}'."
        )
    if username[-1] in "._+-":
        return False, (
            f"Error: Username '{username}' must end with a letter or digit, "
            f"not '{username[-1]}'."
        )

    # No consecutive dots
    if ".." in username:
        return False, (
            f"Error: Username '{username}' contains consecutive dots ('..'), "
            f"which are not allowed."
        )

    return True, f"'{email}' is a valid Gmail address."


# ──────────────────────────────────────────────
#  Interactive driver
# ──────────────────────────────────────────────

def run_tests():
    """Run a pre-defined test suite and print results."""
    ip_tests = [
        "8.8.8.8",           # valid (Google DNS)
        "192.168.1.1",       # private
        "10.0.0.1",          # private
        "256.100.50.25",     # octet out of range
        "172.16.5.10",       # private
        "127.0.0.1",         # loopback
        "999.999.999.999",   # all octets invalid
        "abc.def.ghi.jkl",  # non-numeric
        "192.168.1",         # too few octets
        "01.02.03.04",       # leading zeros
        "203.0.113.45",      # valid (TEST-NET-3, routable outside private)
        "",                  # empty
    ]

    email_tests = [
        "alice.smith@gmail.com",      # valid
        "user+tag@gmail.com",         # valid
        "john_doe123@gmail.com",      # valid
        "noatsign.gmail.com",         # missing @
        "user@yahoo.com",             # wrong domain
        "UPPER@gmail.com",            # uppercase not allowed
        ".leadingdot@gmail.com",      # leading dot
        "trailingdot.@gmail.com",     # trailing dot
        "double..dot@gmail.com",      # consecutive dots
        "ab@gmail.com",               # too short
        "valid123@gmail.com",         # valid
        "",                           # empty
        "special!#@gmail.com",        # invalid symbols
    ]

    sep = "─" * 55

    print("\n" + sep)
    print("  IPv4 VALIDATION RESULTS")
    print(sep)
    for ip in ip_tests:
        ok, msg = validate_ipv4(ip)
        status = "✔ PASS" if ok else "✘ FAIL"
        label = f"  [{status}]  Input: '{ip}'"
        print(f"{label}\n           {msg}\n")

    print(sep)
    print("  GMAIL VALIDATION RESULTS")
    print(sep)
    for email in email_tests:
        ok, msg = validate_gmail(email)
        status = "✔ PASS" if ok else "✘ FAIL"
        label = f"  [{status}]  Input: '{email}'"
        print(f"{label}\n           {msg}\n")


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    run_tests()