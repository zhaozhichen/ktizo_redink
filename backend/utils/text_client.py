"""Create the text client from central configuration only."""
from backend.config import Config
from .genai_client import GenAIClient


def get_text_chat_client(provider_config):
    expected = Config.load_text_providers_config()['providers']['gemini']
    if provider_config != expected:
        raise ValueError('AI provider and model are managed by ktizo_io')
    return GenAIClient(api_key=expected['api_key'])
