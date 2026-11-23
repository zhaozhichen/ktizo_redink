"""Expose central AI configuration for display; do not accept local overrides."""
from flask import Blueprint, jsonify
from backend.config import Config
from .utils import prepare_providers_for_response


def create_config_blueprint():
    bp = Blueprint('config', __name__)

    @bp.get('/config')
    def get_config():
        result = {}
        for kind, config in [('text_generation', Config.load_text_providers_config()),
                             ('image_generation', Config.load_image_providers_config())]:
            result[kind] = {'active_provider': config['active_provider'],
                            'providers': prepare_providers_for_response(config['providers'])}
        return jsonify(success=True, ai_managed=True, config=result)

    @bp.post('/config')
    @bp.post('/config/test')
    def reject_override():
        return jsonify(success=False, error='AI 设置由 ktizo_io 统一管理'), 409

    return bp
