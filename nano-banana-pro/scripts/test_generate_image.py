import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("generate_image.py")
SPEC = importlib.util.spec_from_file_location("generate_image", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize(
    ("max_input_dim", "expected"),
    [
        (0, "1K"),
        (1499, "1K"),
        (1500, "2K"),
        (2999, "2K"),
        (3000, "4K"),
    ],
)
def test_auto_detect_resolution_thresholds(max_input_dim, expected):
    assert MODULE.auto_detect_resolution(max_input_dim) == expected


def test_choose_output_resolution_auto_detects_when_resolution_omitted():
    assert MODULE.choose_output_resolution(None, 2200, True) == ("2K", True)


def test_choose_output_resolution_defaults_to_1k_without_inputs():
    assert MODULE.choose_output_resolution(None, 0, False) == ("1K", False)


def test_choose_output_resolution_respects_explicit_1k_with_large_input():
    assert MODULE.choose_output_resolution("1K", 3500, True) == ("1K", False)


def test_resolve_model_name_uses_default_alias():
    assert MODULE.resolve_model_name(None) == (
        "nano-banana-pro",
        "gemini-3-pro-image-preview",
    )


def test_resolve_model_name_passes_through_unknown_alias():
    assert MODULE.resolve_model_name("some-future-image-model") == (
        "some-future-image-model",
        "some-future-image-model",
    )


def test_resolve_model_name_maps_nano_banana_2_aliases():
    assert MODULE.resolve_model_name("nano-banana-2") == (
        "nano-banana-2",
        "gemini-3.1-flash-image-preview",
    )
    assert MODULE.resolve_model_name("nano-banana-pro2") == (
        "nano-banana-pro2",
        "gemini-3.1-flash-image-preview",
    )


def test_generate_image_file_requires_api_key():
    with pytest.raises(ValueError):
        MODULE.generate_image_file(
            prompt="test",
            filename="out.png",
            api_key=None,
        )
