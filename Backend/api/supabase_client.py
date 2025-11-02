from supabase import create_client
from django.conf import settings

# Create Supabase client using service key (admin access)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
