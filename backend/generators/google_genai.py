"""Google GenAI 图片生成器"""
from backend.config import Config, central_model
import os
import logging
import base64
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from .base import ImageGeneratorBase
from ..utils.image_compressor import compress_image

logger = logging.getLogger(__name__)


def parse_genai_error(error: Exception) -> str:
    """Explain a failure without suggesting independent provider/model settings."""
    message = str(error)
    lower = message.lower()
    if any(token in lower for token in ('429', 'resource_exhausted', '503', 'unavailable')):
        return "AI 服务暂时不可用或已达到限额，请稍后重试。系统会继续使用集中配置的模型。"
    if any(token in lower for token in ('401', '403', 'unauthenticated', 'permission_denied')):
        return "AI 服务认证或权限失败，请检查 ktizo_io 的集中凭据和项目权限。"
    if any(token in lower for token in ('404', 'not_found')):
        return "AI 模型不可用，请检查 ktizo_io/config/ai.env。"
    return f"AI 调用失败：{message[:500]}"


class GoogleGenAIGenerator(ImageGeneratorBase):
    """Google GenAI 图片生成器"""

    def __init__(self, config: Dict[str, Any]):
        if config != Config.get_image_provider_config():
            raise ValueError('AI provider and model are managed by ktizo_io')
        super().__init__(config)
        self.is_vertexai = False
        client_kwargs = {"api_key": self.api_key, "vertexai": False}

        self.client = genai.Client(**client_kwargs)

        # 默认安全设置
        self.safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ]
        logger.info("GoogleGenAIGenerator 初始化完成")

    def validate_config(self) -> bool:
        """验证配置"""
        return bool(self.api_key)

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "3:4",
        temperature: float = 1.0,
        model: str = os.environ["GEMINI_IMAGE_MODEL"],
        reference_image: Optional[bytes] = None,
        **kwargs
    ) -> bytes:
        """
        生成图片

        Args:
            prompt: 提示词
            aspect_ratio: 宽高比 (如 "3:4", "1:1", "16:9")
            temperature: 温度
            model: 模型名称
            reference_image: 参考图片二进制数据（用于保持风格一致）
            **kwargs: 其他参数

        Returns:
            图片二进制数据
        """
        logger.info(f"Google GenAI 生成图片: model={model}, aspect_ratio={aspect_ratio}")
        logger.debug(f"  prompt 长度: {len(prompt)} 字符, 有参考图: {reference_image is not None}")

        # 构建 parts 列表
        parts = []

        # 如果有参考图，先添加参考图和说明
        if reference_image:
            logger.debug(f"  添加参考图片 ({len(reference_image)} bytes)")
            # 压缩参考图到 200KB 以内
            compressed_ref = compress_image(reference_image, max_size_kb=200)
            logger.debug(f"  参考图压缩后: {len(compressed_ref)} bytes")
            # 添加参考图
            parts.append(types.Part(
                inline_data=types.Blob(
                    mime_type="image/png",
                    data=compressed_ref
                )
            ))
            # 添加带参考说明的提示词
            enhanced_prompt = f"""请参考上面这张图片的视觉风格（包括配色、排版风格、字体风格、装饰元素风格），生成一张风格一致的新图片。

新图片的内容要求：
{prompt}

重要：
1. 必须保持与参考图相同的视觉风格和设计语言
2. 配色方案要与参考图协调一致
3. 排版和装饰元素的风格要统一
4. 但内容要按照新的要求来生成"""
            parts.append(types.Part(text=enhanced_prompt))
        else:
            # 没有参考图，直接使用原始提示词
            parts.append(types.Part(text=prompt))

        contents = [
            types.Content(
                role="user",
                parts=parts
            )
        ]

        image_config_kwargs = {
            "aspect_ratio": aspect_ratio,
        }

        # 只有在 Vertex AI 模式下才支持 output_mime_type
        if self.is_vertexai:
            image_config_kwargs["output_mime_type"] = "image/png"

        generate_content_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=0.95,
            max_output_tokens=32768,
            response_modalities=["TEXT", "IMAGE"],
            safety_settings=self.safety_settings,
            image_config=types.ImageConfig(**image_config_kwargs),
        )

        image_data = None
        logger.debug(f"  开始调用 API: model={model}")
        for chunk in self.client.models.generate_content_stream(
            model=central_model("GEMINI_IMAGE_MODEL", model),
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                for part in chunk.candidates[0].content.parts:
                    # 检查是否有图片数据
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        logger.debug(f"  收到图片数据: {len(image_data)} bytes")
                        break

        if not image_data:
            logger.error("API 返回为空，未生成图片")
            raise ValueError(
                "❌ 图片生成失败：API 返回为空\n\n"
                "【可能原因】\n"
                "1. 提示词触发了安全过滤（最常见）\n"
                "2. 模型不支持当前的图片生成请求\n"
                "3. 网络传输过程中数据丢失\n\n"
                "【解决方案】\n"
                "1. 修改提示词，避免敏感内容：\n"
                "   - 避免涉及暴力、血腥、色情等内容\n"
                "   - 避免涉及真实人物（明星、政治人物等）\n"
                "   - 使用更中性、积极的描述\n"
                "2. 尝试简化提示词\n"
                "3. 检查网络连接后重试"
            )

        logger.info(f"✅ Google GenAI 图片生成成功: {len(image_data)} bytes")
        return image_data

    def get_supported_aspect_ratios(self) -> list:
        """获取支持的宽高比"""
        return ["1:1", "3:4", "4:3", "16:9", "9:16"]
