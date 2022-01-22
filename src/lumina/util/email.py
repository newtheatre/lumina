def mask_email(email: str) -> str:
    """
    Masks an email address by replacing the address and domain with *s
    leaving only two characters of each plus the last part of the domain.

    For example:
        fred.bloggs@gmail.com -> fr***@gm***.com
    """
    if email.count("@") != 1:
        raise ValueError("Invalid email address, should have exactly one @")
    address, domain = email.split("@")
    if not address:
        raise ValueError("Invalid email address, address should not be empty")
    if not domain:
        raise ValueError("Invalid email address, domain should not be empty")
    domain_fore, _, domain_tld = domain.rpartition(".")
    if not domain_fore:
        raise ValueError("Invalid email address, cannot work out domain")
    if not domain_tld:
        raise ValueError("Invalid email address, cannot work out domain tld")
    return f"{address[:2]}***@{domain_fore[:2]}***.{domain_tld}"
