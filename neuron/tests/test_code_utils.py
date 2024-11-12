import pytest
from neuron.code_utils import content_str

def test_should_return_empty_string_when_content_is_none():
    content = None
    assert content_str(content) == ""

def test_should_return_content_when_content_is_string():
    content = "Hello, world!"
    assert content_str(content) == content

def test_should_handle_text_content_part():
    content = [{"type": "text", "text": "Hello"}]
    assert content_str(content) == "Hello"

def test_should_handle_image_content_part():
    content = [{"type": "image_url"}]
    assert content_str(content) == "<image>"

def test_should_handle_mixed_content():
    content = [
        {"type": "text", "text": "Hello, "},
        {"type": "image_url"},
        {"type": "text", "text": "world!"}
    ]
    assert content_str(content) == "Hello, <image>world!"

def test_should_raise_type_error_on_invalid_content():
    content = 123  # Invalid type
    with pytest.raises(TypeError, match="content must be None, str, or list"):
        content_str(content)

def test_should_raise_type_error_on_invalid_list_element():
    content = ["not_a_dict"]  # Invalid element in list
    with pytest.raises(TypeError, match="Wrong content format: every element should be dict"):
        content_str(content)

def test_should_raise_assertion_error_on_missing_type_key():
    content = [{}]  # Missing "type" key
    with pytest.raises(AssertionError, match="Wrong content format. Missing 'type' key in content's dict."):
        content_str(content)

def test_should_raise_value_error_on_unknown_type():
    content = [{"type": "unknown", "text": "Hello"}]  # Invalid "type" value
    with pytest.raises(ValueError, match="Wrong content format: unknown type unknown within the content"):
        content_str(content)
