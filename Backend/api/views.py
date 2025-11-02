from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .auth_utils import verify_supabase_token
from supabase import create_client
from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@api_view(['GET'])
def get_profile(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"error": "Missing or invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(" ")[1]
    user_data = verify_supabase_token(token)

    if not user_data:
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

    # Use user ID or email from the verified token
    user_email = user_data.get("email")

    # Example: fetch user data from your Supabase table
    response = supabase.table("users").select("*").eq("email", user_email).execute()

    if not response.data:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(response.data[0], status=status.HTTP_200_OK)
