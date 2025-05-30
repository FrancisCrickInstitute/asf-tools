"""
WebhookLogger: A helper library for logging events to webhooks with rich formatting and configurable features.
"""

import json
from enum import Enum, auto
from typing import Dict, List, Optional

import requests


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
    def section(
        text: str = None,
        fields: Optional[List[str]] = None,
        mentions: Optional[List[str]] = None,
        resolver: "SlackUserResolver" = None,
    ) -> "WebhookBlock":
        """
        Create a section block. If fields are provided, they are formatted as mrkdwn fields.
        Optionally prepend Slack user mentions to the text. Usernames are resolved if a resolver is provided.
        :param text: The section text (mrkdwn)
        :param fields: List of field strings (mrkdwn)
        :param mentions: List of Slack user IDs or usernames to mention
        :param resolver: Optional SlackUserResolver for username resolution
        :return: WebhookBlock
        """
        block_kwargs = {}
        mention_str = ""
        if mentions:
            mention_ids = []
            for m in mentions:
                if resolver:
                    uid = resolver.resolve(m)
                    if uid:
                        mention_ids.append(uid)
                    else:
                        mention_ids.append(m)
                else:
                    mention_ids.append(m)
            if mention_ids:
                mention_str = " ".join(f"<@{uid}>" for uid in mention_ids) + " "
        if text:
            block_kwargs["text"] = {"type": "mrkdwn", "text": f"{mention_str}{text}"}
        if fields:
            block_kwargs["fields"] = [{"type": "mrkdwn", "text": f} for f in fields]
        return WebhookBlock(BlockType.SECTION, **block_kwargs)

    @staticmethod
    def context(
        elements: List[str],
        mentions: Optional[List[str]] = None,
        resolver: "SlackUserResolver" = None,
    ) -> "WebhookBlock":
        """
        Create a context block with mrkdwn elements. Optionally prepend Slack user mentions to each element.
        Usernames are resolved if a resolver is provided.
        :param elements: List of context strings (mrkdwn)
        :param mentions: List of Slack user IDs or usernames to mention
        :param resolver: Optional SlackUserResolver for username resolution
        :return: WebhookBlock
        """
        mention_str = ""
        if mentions:
            mention_ids = []
            for m in mentions:
                if resolver:
                    uid = resolver.resolve(m)
                    if uid:
                        mention_ids.append(uid)
                    else:
                        mention_ids.append(m)
                else:
                    mention_ids.append(m)
            if mention_ids:
                mention_str = " ".join(f"<@{uid}>" for uid in mention_ids) + " "
        return WebhookBlock(
            BlockType.CONTEXT,
            elements=[{"type": "mrkdwn", "text": f"{mention_str}{e}"} for e in elements],
        )

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
            prefix = "... (truncated)\n"
            if len(text) > max_chars:
                # Only take the last (max_chars - len(prefix)) chars, then prepend prefix
                truncated = text[-(max_chars - len(prefix)) :] if max_chars > len(prefix) else ""
                code = f"```{prefix}{truncated}```"
            else:
                code = f"```{text}```"
        return WebhookBlock.section(text=code)

    @staticmethod
    def build_payload(blocks: list["WebhookBlock"]) -> dict:
        """
        Helper to build a Slack payload from a list of WebhookBlock objects.
        :param blocks: List of WebhookBlock instances
        :return: Dict payload suitable for Slack webhook
        """
        return {"blocks": [block.to_dict() for block in blocks]}


class SlackUserResolver:
    """
    Resolves Slack usernames to user IDs using the Slack Web API.
    No caching is performed; each lookup makes an API call.
    """

    def __init__(self, token: str):
        self.token = token

    def resolve(self, username: str) -> Optional[str]:
        """
        Resolve a Slack username (without @) to a user ID using the Slack API.
        Returns None if not found or on error.
        """
        url = "https://slack.com/api/users.list"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                return None
            for member in data.get("members", []):
                # Clean and normalize the name
                name = member.get("profile").get("display_name_normalized").lower()
                if name is None or name == "":
                    name = member.get("profile").get("real_name_normalized").lower().replace(" ", ".")

                # Match the name
                if name == username.lower():
                    return member.get("id")
        except (requests.RequestException, ValueError, KeyError):
            return None
        return None


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
