"""LLM service abstraction layer."""
import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from openai import OpenAI


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def stream(self, messages: List[Dict[str, str]], **kwargs):
        """Stream a response from the LLM."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ''
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def stream(self, messages: List[Dict[str, str]], **kwargs):
        """Stream response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **kwargs
            )
            for chunk in response:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from Anthropic."""
        # Anthropic implementation would go here
        raise NotImplementedError("Anthropic provider not yet implemented")

    def stream(self, messages: List[Dict[str, str]], **kwargs):
        """Stream response from Anthropic."""
        # Anthropic streaming implementation would go here
        raise NotImplementedError("Anthropic streaming not yet implemented")


class LLMFactory:
    """Factory for creating LLM providers."""
    
    _providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
    }

    @classmethod
    def create(cls, provider: str, **kwargs) -> BaseLLMProvider:
        """Create an LLM provider instance."""
        provider_class = cls._providers.get(provider.lower())
        if not provider_class:
            raise ValueError(f"Unknown LLM provider: {provider}")
        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class):
        """Register a new LLM provider."""
        cls._providers[name.lower()] = provider_class
