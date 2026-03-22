# get_token.py
# Certificate-based authentication for epautomation@irco.com
# Uses MSAL client credentials flow with certificate

import msal
import os
import sys

def get_access_token():
    """
    Acquires an access token using certificate-based client credentials.
    Reads all config from environment variables (set via GitHub Secrets).
    """
    tenant_id   = os.environ["AZURE_TENANT_ID"]
    client_id   = os.environ["AZURE_CLIENT_ID"]
    private_key = os.environ["EPAUTOMATION_PRIVATE_KEY"]
    thumbprint  = os.environ["CERT_THUMBPRINT"]
    scope       = os.environ.get("AUTH_SCOPE", "https://graph.microsoft.com/.default")

    # Build the ConfidentialClientApplication with certificate credentials
    app = msal.ConfidentialClientApplication(
        client_id  = client_id,
        authority  = f"https://login.microsoftonline.com/{tenant_id}",
        client_credential = {
            "private_key": private_key,
            "thumbprint":  thumbprint,
        }
    )

    # Try cache first, then get fresh token from Azure AD
    result = app.acquire_token_silent(scopes=[scope], account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=[scope])

    if "access_token" not in result:
        error = result.get("error", "unknown")
        desc  = result.get("error_description", "No description")
        print(f"Authentication failed: {error} — {desc}", file=sys.stderr)
        sys.exit(1)

    return result["access_token"]

if __name__ == "__main__":
    token = get_access_token()
    print(token)
