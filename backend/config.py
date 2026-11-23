"""Read-only AI roles injected from ktizo_io/config/ai.env."""
import os
from copy import deepcopy


def central_model(role, requested=None):
    value = os.environ[role]
    if not value or (requested is not None and requested != value):
        raise ValueError(f"{role} is managed by ktizo_io/config/ai.env")
    return value


class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 12398
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']
    OUTPUT_DIR = 'output'
    MAX_CONTENT_LENGTH = 512 * 1024 * 1024

    @classmethod
    def _load_from_env(cls):
        key = os.environ['GEMINI_API_KEY']
        if not key:
            raise ValueError('GEMINI_API_KEY must be injected by ktizo_io')
        text = {'active_provider': 'gemini', 'providers': {'gemini': {
            'type': 'google_gemini', 'api_key': key,
            'model': central_model('GEMINI_MULTIMODAL_MODEL'),
            'temperature': 1.0, 'max_output_tokens': 8000}}}
        image = {'active_provider': 'gemini', 'providers': {'gemini': {
            'type': 'google_genai', 'api_key': key,
            'model': central_model('GEMINI_IMAGE_MODEL'),
            'high_concurrency': os.getenv('GEMINI_HIGH_CONCURRENCY', 'false').lower() == 'true'}}}
        return text, image

    @classmethod
    def load_text_providers_config(cls):
        return deepcopy(cls._load_from_env()[0])

    @classmethod
    def load_image_providers_config(cls):
        return deepcopy(cls._load_from_env()[1])

    @classmethod
    def get_active_image_provider(cls):
        return 'gemini'

    @classmethod
    def get_image_provider_config(cls, provider_name=None):
        if provider_name not in (None, 'gemini'):
            raise ValueError('AI provider is managed by ktizo_io')
        return cls.load_image_providers_config()['providers']['gemini']

    @classmethod
    def reload_config(cls):
        cls._load_from_env()
