def get_api_token():
    """Read the token from the OS keyring without crashing on locked/missing backends."""
    try:
        import keyring
        return keyring.get_password("UA Alert", "api_token") or ""
    except Exception:
        return ""
