"""
Test suite for the WebhookLogger helper library.
Covers event logging, formatting, and delivery features.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member


from assertpy import assert_that

from asf_tools.slack.webhook_logger import EventCategory, WebhookBlock, WebhookEvent, WebhookLogger


def test_slack_webhook_logger_header_block():
    block = WebhookBlock.header("Pipeline Complete")
    assert_that(block.to_dict()).is_equal_to({"type": "header", "text": {"type": "plain_text", "text": "Pipeline Complete"}})


def test_slack_webhook_logger_divider_block():
    block = WebhookBlock.divider()
    assert_that(block.to_dict()).is_equal_to({"type": "divider"})


def test_slack_webhook_logger_section_block_with_text():
    block = WebhookBlock.section(text="*Hello* _World_ :rocket:")
    assert_that(block.to_dict()).is_equal_to({"type": "section", "text": {"type": "mrkdwn", "text": "*Hello* _World_ :rocket:"}})


def test_slack_webhook_logger_section_block_with_fields():
    fields = ["*Pipeline:*\n`daily-report`", "*Status:*\n:white_check_mark: Success"]
    block = WebhookBlock.section(fields=fields)
    assert_that(block.to_dict()).is_equal_to(
        {"type": "section", "fields": [{"type": "mrkdwn", "text": fields[0]}, {"type": "mrkdwn", "text": fields[1]}]}
    )


def test_slack_webhook_logger_context_block():
    elements = ["View the full report: <https://ci.example.com/report|CI Report>"]
    block = WebhookBlock.context(elements)
    assert_that(block.to_dict()).is_equal_to({"type": "context", "elements": [{"type": "mrkdwn", "text": elements[0]}]})


def test_slack_webhook_logger_image_block():
    block = WebhookBlock.image("https://img.png", "alt text")
    assert_that(block.to_dict()).is_equal_to({"type": "image", "image_url": "https://img.png", "alt_text": "alt text"})


def test_slack_webhook_logger_alert_text_icons():
    text = WebhookBlock.alert_text(EventCategory.SUCCESS, "All good!")
    assert_that(text).contains("✅").contains("*SUCCESS*:")
    text = WebhookBlock.alert_text(EventCategory.FAILURE, "Failed!")
    assert_that(text).contains("❌").contains("*FAILURE*:")
    text = WebhookBlock.alert_text(EventCategory.INFO, "FYI")
    assert_that(text).contains("ℹ️").contains("*INFO*:")
    text = WebhookBlock.alert_text(EventCategory.WARNING, "Careful!")
    assert_that(text).contains("⚠️").contains("*WARNING*:")
    text = WebhookBlock.alert_text(EventCategory.ERROR, "Error!")
    assert_that(text).contains("🛑").contains("*ERROR*:")
    text = WebhookBlock.alert_text(EventCategory.CRITICAL, "Critical!")
    assert_that(text).contains("🚨").contains("*CRITICAL*:")


def test_slack_webhook_logger_webhook_event_to_payload():
    blocks = [
        WebhookBlock.header("Test Header"),
        WebhookBlock.section(text=WebhookBlock.alert_text(EventCategory.INFO, "Test message")),
        WebhookBlock.divider(),
    ]
    event = WebhookEvent(blocks=blocks)
    payload = event.to_payload()
    assert_that(payload).contains_key("blocks")
    assert_that(payload["blocks"]).is_length(3)
    assert_that(payload["blocks"][0]["type"]).is_equal_to("header")
    assert_that(payload["blocks"][1]["type"]).is_equal_to("section")
    assert_that(payload["blocks"][2]["type"]).is_equal_to("divider")


def test_slack_webhook_logger_webhook_logger_posts_payload(monkeypatch):
    logger = WebhookLogger(webhook_urls={"default": "https://example.com/webhook"})
    blocks = [WebhookBlock.header("Test")]
    event = WebhookEvent(blocks=blocks)
    payload = event.to_payload()
    called = {}

    def fake_post(url, headers, data, timeout):
        called["url"] = url
        called["headers"] = headers
        called["data"] = data
        called["timeout"] = timeout

        class Resp:
            pass

        return Resp()

    monkeypatch.setattr("requests.post", fake_post)
    logger.log_event(payload)
    assert_that(called["url"]).is_equal_to("https://example.com/webhook")
    assert_that(called["headers"]["Content-Type"]).is_equal_to("application/json")
    assert_that(called["timeout"]).is_equal_to(10)
    assert_that(called["data"]).contains("Test")


def test_slack_webhook_logger_code_block_with_text():
    code = "print('hello world')\nprint('goodbye')"
    block = WebhookBlock.code_block(code)
    assert_that(block.to_dict()).is_equal_to({"type": "section", "text": {"type": "mrkdwn", "text": "```print('hello world')\nprint('goodbye')```"}})


def test_slack_webhook_logger_code_block_with_empty_text():
    block = WebhookBlock.code_block("")
    assert_that(block.to_dict()).is_equal_to({"type": "section", "text": {"type": "mrkdwn", "text": "`<no output>`"}})


def test_slack_webhook_logger_code_block_with_whitespace():
    code = "  line1\n  line2  \n"
    block = WebhookBlock.code_block(code)
    assert_that(block.to_dict()).is_equal_to({"type": "section", "text": {"type": "mrkdwn", "text": "```  line1\n  line2  \n```"}})


def test_slack_webhook_logger_code_block_truncation():
    code = "A" * 3000
    block = WebhookBlock.code_block(code, max_chars=2500)
    out = block.to_dict()["text"]["text"]
    assert out.startswith("```... (truncated)\n")
    assert out.endswith("```")
    assert len(out) <= 2515  # 2500 chars + prefix + triple backticks
