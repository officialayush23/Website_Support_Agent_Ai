import requests
from django.conf import settings

def verify_supabase_token(token: str):
    """
    Verify a Supabase JWT by calling /auth/v1/user endpoint.
    Returns user object if valid, else None.
    """
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{settings.SUPABASE_URL}/auth/v1/user", headers=headers)
    
    if response.status_code == 200:
        return response.json()  # includes id, email, role, etc.
    return None
