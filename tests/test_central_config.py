import os
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from flask import Flask
from backend.config import Config
from backend.routes.config_routes import create_config_blueprint

class CentralConfigTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ, GEMINI_API_KEY='synthetic-key', GEMINI_MULTIMODAL_MODEL='central-text', GEMINI_IMAGE_MODEL='central-image', KTIZO_AI_MANAGED='false')
        self.env.start(); self.addCleanup(self.env.stop)
        self.app=Flask(__name__); self.app.register_blueprint(create_config_blueprint(),url_prefix='/api')
        self.client=self.app.test_client()
    def test_configuration_is_readonly_even_without_managed_flag(self):
        response=self.client.get('/api/config')
        self.assertEqual(response.status_code,200)
        data=response.get_json(); self.assertTrue(data['ai_managed'])
        self.assertEqual(data['config']['text_generation']['providers']['gemini']['model'],'central-text')
        self.assertNotIn('synthetic-key', response.get_data(as_text=True))
        for url in ['/api/config','/api/config/test']:
            self.assertEqual(self.client.post(url,json={'model':'override','api_key':'other'}).status_code,409)
    def test_missing_central_role_does_not_read_yaml(self):
        del os.environ['GEMINI_IMAGE_MODEL']
        with self.assertRaises(KeyError): Config.load_image_providers_config()
    def test_rejects_other_provider(self):
        with self.assertRaises(ValueError): Config.get_image_provider_config('openai')
    def test_clients_reject_override_before_sdk_initialization(self):
        from backend.generators.google_genai import GoogleGenAIGenerator
        from backend.utils.genai_client import GenAIClient
        config=Config.get_image_provider_config(); config['model']='override'
        with patch('backend.generators.google_genai.genai.Client') as sdk:
            with self.assertRaises(ValueError): GoogleGenAIGenerator(config)
            with self.assertRaises(ValueError): GenAIClient(api_key='different')
            sdk.assert_not_called()
    def test_text_call_uses_central_role_and_rejects_override(self):
        from backend.utils.genai_client import GenAIClient
        with patch('backend.utils.genai_client.genai.Client') as sdk:
            client=GenAIClient()
            sdk.return_value.models.generate_content_stream.return_value=[SimpleNamespace(text='ok',candidates=[SimpleNamespace(content=SimpleNamespace(parts=['ok']))])]
            self.assertEqual(client.generate_text.__wrapped__(client,'hello',model='central-text'),'ok')
            self.assertEqual(sdk.return_value.models.generate_content_stream.call_args.kwargs['model'],'central-text')
            sdk.return_value.models.generate_content_stream.reset_mock()
            with self.assertRaises(ValueError): client.generate_text.__wrapped__(client,'hello',model='override')
            sdk.return_value.models.generate_content_stream.assert_not_called()

    def test_image_service_uses_central_factory(self):
        from backend.services.image import ImageService
        with patch('backend.generators.google_genai.genai.Client'):
            service=ImageService()
            self.assertEqual(service.provider_config['model'],'central-image')
            self.assertEqual(service.generator.config['model'],'central-image')
