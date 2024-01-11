from settings import SupabaseEnvVars
from supabase import create_client, Client


def create_supabase_client() -> Client:
    supabaseEnvVars = SupabaseEnvVars()
    supabase_client: Client = create_client(supabaseEnvVars.supabase_url, supabaseEnvVars.supabase_service_key)
    return supabase_client
