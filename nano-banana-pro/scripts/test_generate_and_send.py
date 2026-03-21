import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("generate_and_send.py")
SPEC = importlib.util.spec_from_file_location("generate_and_send", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_message_send_command_with_caption_and_account():
    command = MODULE.build_message_send_command(
        channel="dingtalk",
        target="user:1112014757-2075222354",
        media_path=Path("/tmp/test.png"),
        caption="hello",
        account="default",
    )
    assert command == [
        "openclaw",
        "message",
        "send",
        "--channel",
        "dingtalk",
        "--target",
        "1112014757-2075222354",
        "--media",
        "/tmp/test.png",
        "--json",
        "--message",
        "hello",
        "--account",
        "default",
    ]


def test_normalize_send_target_strips_dingtalk_prefixes():
    assert MODULE.normalize_send_target("dingtalk", "user:abc") == "abc"
    assert MODULE.normalize_send_target("dingtalk", "group:cid123") == "cid123"
    assert MODULE.normalize_send_target("telegram", "user:abc") == "user:abc"


def test_build_message_send_command_without_optional_fields():
    command = MODULE.build_message_send_command(
        channel="dingtalk",
        target="cidExampleBase64Id",
        media_path=Path("/tmp/test.png"),
        caption=None,
        account=None,
    )
    assert command == [
        "openclaw",
        "message",
        "send",
        "--channel",
        "dingtalk",
        "--target",
        "cidExampleBase64Id",
        "--media",
        "/tmp/test.png",
        "--json",
    ]
