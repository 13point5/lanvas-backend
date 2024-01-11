from pydantic_settings import BaseSettings


class SupabaseEnvVars(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    supabase_jwt_secret_key: str


class OpenAIEnvVars(BaseSettings):
    openai_api_key: str
