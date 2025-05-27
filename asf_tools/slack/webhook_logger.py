"""
WebhookLogger: A helper library for logging events to webhooks with rich formatting and configurable features.
"""
import requests
from enum import Enum, auto
from typing import Dict, Optional, List
import json

class EventCategory(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

class BlockType(Enum):
    HEADER = "header"
    DIVIDER = "divider"
    SECTION = "section"
    CONTEXT = "context"
    IMAGE = "image"
    ACTIONS = "actions"
    # Add more Slack block types as needed

class WebhookBlock:
    def __init__(self, block_type: BlockType, **kwargs):
        """
        Represents a single Slack block.
        :param block_type: The type of block (from BlockType enum)
        :param kwargs: Block-specific fields (e.g., text, fields, elements)
        """
        self.block_type = block_type
        self.kwargs = kwargs

    def to_dict(self) -> dict:
        block = {"type": self.block_type.value}
        block.update(self.kwargs)
        return block

    @staticmethod
    def header(text: str) -> "WebhookBlock":
        """
        Create a header block.
        :param text: The header text (plain_text)
        :return: WebhookBlock
        """
        return WebhookBlock(BlockType.HEADER, text={"type": "plain_text", "text": text.replace("*", "")})

    @staticmethod
    def divider() -> "WebhookBlock":
        """
        Create a divider block.
        :return: WebhookBlock
        """
        return WebhookBlock(BlockType.DIVIDER)

    @staticmethod
    def section(text: str = None, fields: Optional[List[str]] = None) -> "WebhookBlock":
        """
        Create a section block. If fields are provided, they are formatted as mrkdwn fields.
        :param text: The section text (mrkdwn)
        :param fields: List of field strings (mrkdwn)
        :return: WebhookBlock
        """
        block_kwargs = {}
        if text:
            block_kwargs["text"] = {"type": "mrkdwn", "text": text}
        if fields:
            block_kwargs["fields"] = [{"type": "mrkdwn", "text": f} for f in fields]
        return WebhookBlock(BlockType.SECTION, **block_kwargs)

    @staticmethod
    def context(elements: List[str]) -> "WebhookBlock":
        """
        Create a context block with mrkdwn elements.
        :param elements: List of context strings (mrkdwn)
        :return: WebhookBlock
        """
        return WebhookBlock(BlockType.CONTEXT, elements=[{"type": "mrkdwn", "text": e} for e in elements])

    @staticmethod
    def image(image_url: str, alt_text: str) -> "WebhookBlock":
        """
        Create an image block.
        :param image_url: The image URL
        :param alt_text: The alt text for the image
        :return: WebhookBlock
        """
        return WebhookBlock(BlockType.IMAGE, image_url=image_url, alt_text=alt_text)

    @staticmethod
    def alert_text(level: EventCategory, text: str) -> str:
        """
        Format text with an alert level and icon.
        :param level: The EventCategory (e.g., SUCCESS, FAILURE, INFO, etc.)
        :param text: The message text
        :return: Formatted string with icon and level
        """
        icons = {
            EventCategory.SUCCESS: "✅",
            EventCategory.FAILURE: "❌",
            EventCategory.INFO: "ℹ️",
            EventCategory.WARNING: "⚠️",
            EventCategory.ERROR: "🛑",
            EventCategory.CRITICAL: "🚨",
        }
        icon = icons.get(level, "")
        return f"{icon} *{level.name}*: {text}"

    @staticmethod
    def code_block(text: str, max_chars: int = 2500) -> "WebhookBlock":
        """
        Create a section block that renders the given text as a code block in Slack (using triple backticks).
        Shows the last max_chars characters from the text (default 2500).
        :param text: The code or log text to display
        :param max_chars: Maximum number of characters to display (default 2500)
        :return: WebhookBlock
        """
        if not text:
            code = "`<no output>`"
        else:
            prefix = '... (truncated)\n'
            if len(text) > max_chars:
                # Only take the last (max_chars - len(prefix)) chars, then prepend prefix
                truncated = text[-(max_chars - len(prefix)):] if max_chars > len(prefix) else ''
                code = f'```{prefix}{truncated}```'
            else:
                code = f'```{text}```'
        return WebhookBlock.section(text=code)

class WebhookEvent:
    def __init__(
        self,
        blocks: Optional[List[WebhookBlock]] = None,
    ):
        self.blocks = blocks or []

    def to_payload(self) -> dict:
        return {"blocks": [block.to_dict() for block in self.blocks]}

class WebhookLogger:
    def __init__(
        self,
        webhook_urls: Dict[str, str],
    ):
        """
        :param webhook_urls: Dict of endpoint names to URLs
        :param default_category: Default event category
        """
        self.webhook_urls = webhook_urls

    def log_event(self, payload: dict, endpoint: str = "default"):
        """
        Log an event to the specified webhook endpoint using a rich block payload.

        :param payload: The Slack block payload to send.
        :param endpoint: The webhook endpoint key to use.
        """
        self._send_to_webhook(payload, endpoint)

    def _send_to_webhook(self, payload: dict, endpoint: str = "default"):
        """
        Send the formatted payload to the specified webhook endpoint using JSON and explicit headers.

        :param payload: The payload dictionary to send.
        :param endpoint: The webhook endpoint key to use.
        """
        url = self.webhook_urls.get(endpoint)
        if not url:
            raise ValueError(f"No webhook URL configured for endpoint '{endpoint}'")
        headers = {"Content-Type": "application/json"}
        requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
