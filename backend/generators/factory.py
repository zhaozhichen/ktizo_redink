"""Only the centrally configured Google image provider is supported."""
from backend.config import Config
from .google_genai import GoogleGenAIGenerator


class ImageGeneratorFactory:
    @classmethod
    def create(cls, provider, config):
        if provider != 'google_genai' or config != Config.get_image_provider_config():
            raise ValueError('AI provider and model are managed by ktizo_io')
        return GoogleGenAIGenerator(Config.get_image_provider_config())
