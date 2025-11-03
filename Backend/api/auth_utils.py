import requests
from django.conf import settings

def verify_supabase_token(token: str):
    """
    Verify Supabase JWT using the /auth/v1/user endpoint.
    Returns the user object if valid, else None.
    """
    if not token:
        return None

    url = f"{settings.SUPABASE_URL}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY,  # important!
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            print("Supabase verification failed:", res.text)
            return None
    except requests.RequestException as e:
        print("Supabase request error:", e)
        return None
