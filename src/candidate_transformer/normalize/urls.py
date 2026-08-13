from urllib.parse import urlparse

def classify_url(raw: str) -> tuple[str, str] | None:
    if not raw or not isinstance(raw, str):
        return None
    cleaned = raw.strip()
    
    # Fast fail for obvious non-URLs (like plain text with spaces)
    if " " in cleaned:
        return None
        
    if not cleaned.startswith(("http://", "https://")):
        cleaned = "https://" + cleaned
        
    try:
        parsed = urlparse(cleaned)
        # Require a network location and a TLD dot
        if not parsed.netloc or "." not in parsed.netloc:
            return None
            
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
            
        # Reconstruct without tracking params
        clean_url = f"{parsed.scheme}://{host}{parsed.path}".rstrip("/")
        
        if "linkedin.com" in host:
            return ("linkedin", clean_url)
        elif "github.com" in host:
            return ("github", clean_url)
        else:
            return ("portfolio", clean_url)
    except Exception:
        return None