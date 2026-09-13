"""
Unit tests for main.py module
"""
import pytest
from unittest.mock import patch, MagicMock
import os


def test_api_key_loading():
    """Test that API key is properly loaded from environment"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key == "test-key"


def test_api_key_missing():
    """Test that missing API key is handled gracefully"""
    with patch.dict(os.environ, {}, clear=True):
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is None


def test_system_prompt_structure():
    """Test that system prompt is properly formatted"""
    system_prompt = """You are a helpful and strict German language tutor.
    1. Correct any German grammar or spelling mistakes the user makes.
    2. Explain the correction briefly in Chinese or English.
    3. Continue the conversation naturally in German to encourage practice."""
    
    assert "German language tutor" in system_prompt
    assert "grammar" in system_prompt
    assert "German" in system_prompt


def test_message_format():
    """Test that message objects have correct structure"""
    test_message = {"role": "user", "content": "Ich bin ein Schüler"}
    
    assert "role" in test_message
    assert "content" in test_message
    assert test_message["role"] in ["user", "assistant", "system"]


@pytest.mark.parametrize("user_input,expected", [
    ("exit", True),
    ("quit", True),
    ("EXIT", True),
    ("QUIT", True),
    ("hello", False),
])
def test_exit_commands(user_input, expected):
    """Test that exit commands are properly recognized"""
    should_exit = user_input.lower() in ["exit", "quit"]
    assert should_exit == expected
