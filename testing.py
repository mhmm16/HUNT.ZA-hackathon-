import ipaddress
import dns.resolver

# Load TLDs
with open("tldnames.txt", "r") as file:
    tlds = [l.strip().upper() for l in file]  # Force uppercase for consistency

def isTLD(str_val):
    return str_val.upper() in tlds

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

def has_rfc1918_dns(domain: str) -> bool:
    """
    Checks if the domain's mail systems point to private RFC 1918 IPs.
    """
    try:
        # Convert International Domain Names (IDN) to Punycode ascii
        ascii_domain = idnConversion(domain)
        
        target_domains = []
        
        # 1. Try to fetch MX (Mail Exchanger) records first
        try:
            mx_records = dns.resolver.resolve(ascii_domain, 'MX')
            for rdata in mx_records:
                target_domains.append(rdata.exchange.to_text().strip('.'))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            # If no MX records exist, email servers fallback to the root domain A record
            target_domains.append(ascii_domain)

        # 2. Resolve the targeted domains to IPv4 addresses
        for target in target_domains:
            try:
                a_records = dns.resolver.resolve(target, 'A')
                for rdata in a_records:
                    ip_str = rdata.to_text()
                    ip_obj = ipaddress.ip_address(ip_str)
                    
                    # Flag if the resolved target is a private network IP
                    if ip_obj.is_private:
                        return True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                continue
                
    except Exception:
        # Catch network timeouts, formatting drops, or dead domains
        return False
        
    return False

def is_valid(email):
    # Basic structural check for exactly one '@' split
    if "@" not in email or email.count("@") != 1:
        return False

    local, domain = email.split("@")

    # Local-part syntax check
    if not validString(local):
        return False

    # Domain syntax check
    parts = domain.split(".")
    if len(parts) < 2:  # Must have at least a name and a TLD
        return False
        
    for p in parts:
        if not validString(p):
            return False
        
    if not isTLD(parts[-1]):
        return False

    # Network-level check: Verify domain does not route to an internal RFC 1918 IP
    if has_rfc1918_dns(domain):
        print(f"Skipping {email}: Resolves to a private network space.")
        return False

    return True

# --- Test Executions ---
print(is_valid("a@google.com"))     # True (Valid syntax, valid public DNS)
print(is_valid("admin@localhost"))  # False (Fails TLD check or routes to 127.0.0.1)
