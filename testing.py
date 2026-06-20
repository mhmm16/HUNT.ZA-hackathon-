import ipaddress
from collections import defaultdict

import dns.resolver


# ---------------------------------------------------------------------------
# TLD lookup: bucket-by-first-letter + manual binary search
# ---------------------------------------------------------------------------
# Built ONCE at import time. Each bucket is sorted ONCE here, not on every
# call -- sorting per-lookup (as in the original `validate()` snippet) turns
# every check into O(n log n) and erases the benefit of binary search.

def _load_tld_map(path="tldnames.txt"):
    tld_map = defaultdict(list)
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().upper()
            if not line or line.startswith("#"):
                continue
            tld_map[line[0]].append(line)

    for bucket in tld_map.values():
        bucket.sort()

    return dict(tld_map)


TLD_MAP = _load_tld_map()


def manual_binary_search(sorted_list, target):
    low = 0
    high = len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        guess = sorted_list[mid]
        if guess == target:
            return mid
        elif guess > target:
            high = mid - 1
        else:
            low = mid + 1
    return -1


def isTLD(str_val):
    """O(log n) TLD membership check via first-letter bucket + binary search."""
    if not str_val:
        return False

    tld = str_val.upper()
    bucket = TLD_MAP.get(tld[0])
    if not bucket:
        return False

    return manual_binary_search(bucket, tld) != -1


# ---------------------------------------------------------------------------
# Local-part / domain-label syntax
# ---------------------------------------------------------------------------

def validString(str_val):
    length = len(str_val)
    if length == 0:
        return False

    for i, letter in enumerate(str_val):
        if letter == "@":
            return False
        if i == 0 and letter == ".":
            return False
        if (not letter.isalnum() and letter not in ["!", "#", "$", "%", "&", "'", "*", "+", "-", "/", "=", "?", "^", "_", "`", "{", "|", "}", "~", "."]):
            return False
    return True


def idnConversion(str_val):
    return str_val.encode("idna").decode("ascii")


# ---------------------------------------------------------------------------
# RFC 5321 address literals: user@[192.168.1.1]  or  user@[IPv6:2001:db8::1]
# ---------------------------------------------------------------------------

def parse_address_literal(domain: str):
    """
    If `domain` is in RFC 5321 address-literal form ('[' ... ']'),
    return the parsed ip_address object. Otherwise return None
    (meaning: treat `domain` as a normal dotted hostname instead).
    """
    if not (domain.startswith("[") and domain.endswith("]")):
        return None

    inner = domain[1:-1]
    if inner.upper().startswith("IPV6:"):
        inner = inner[5:]

    try:
        return ipaddress.ip_address(inner)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# DNS-based private-network check (for normal hostnames, not literals)
# ---------------------------------------------------------------------------

def has_rfc1918_dns(domain: str) -> bool:
    """
    Checks if the domain's mail systems point to private RFC 1918 IPs.
    """
    try:
        ascii_domain = idnConversion(domain)
        target_domains = []

        try:
            mx_records = dns.resolver.resolve(ascii_domain, 'MX')
            for rdata in mx_records:
                target_domains.append(rdata.exchange.to_text().strip('.'))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            target_domains.append(ascii_domain)

        for target in target_domains:
            try:
                a_records = dns.resolver.resolve(target, 'A')
                for rdata in a_records:
                    ip_str = rdata.to_text()
                    ip_obj = ipaddress.ip_address(ip_str)
                    if ip_obj.is_private:
                        return True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                continue

    except Exception:
        return False

    return False


# ---------------------------------------------------------------------------
# Top-level validator
# ---------------------------------------------------------------------------

def is_valid(email):
    if "@" not in email or email.count("@") != 1:
        return False

    local, domain = email.split("@")

    if not validString(local):
        return False

    # Address-literal domain: skip dotted-label/TLD parsing entirely and
    # judge the IP directly instead of going through DNS.
    literal_ip = parse_address_literal(domain)
    if literal_ip is not None:
        if literal_ip.is_private:
            print(f"Skipping {email}: address literal resolves to a private network space.")
            return False
        return True

    # Normal dotted-hostname domain
    parts = domain.split(".")
    if len(parts) < 2:
        return False

    for p in parts:
        if not validString(p):
            return False

    if not isTLD(parts[-1]):
        return False

    if has_rfc1918_dns(domain):
        print(f"Skipping {email}: Resolves to a private network space.")
        return False

    return True


# --- Test Executions ---
if __name__ == "__main__":
    print(is_valid("a@google.com"))                      # True  (valid syntax, public DNS)
    print(is_valid("admin@localhost"))                    # False (fails TLD check)
    print(is_valid("user@[192.168.1.1]"))                 # False (private IPv4 literal)
    print(is_valid("user@[1.1.1.1]"))                     # True  (public IPv4 literal)
    print(is_valid("user@[IPv6:2606:4700:4700::1111]"))   # True  (public IPv6 literal)
    print(is_valid("user@[IPv6:::1]"))                    # False (loopback IPv6 literal)
    print(is_valid("user@[not-an-ip]"))                   # False (malformed literal)
