"""API Chats gateway."""

import asyncio
import hashlib
import hmac
import json
import time
from email.utils import formatdate
from uuid import uuid4

import httpx
from amocrm.v2 import Contact
from amocrm.v2.interaction import BaseInteraction
from env_settings import env


def singleton(cls):
    """Create a singleton instance of a class."""
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class ChatsAPI:
    def __init__(self) -> None:
        self.channel_secret = env.AMOCRM_CHANNEL_SECRET
        self.channel_id = env.AMOCRM_CHANNEL_ID
        self.base_url = "https://amojo.amocrm.ru"
        self.scope_id = env.AMOCRM_SCOPE_ID
        self.bot_id = env.AMOCRM_BOT_ID
        self.bot_client_id = env.AMOCRM_BOT_CLIENT_ID
        self.bot_name = env.AMOCRM_BOT_NAME

    def __create_body_checksum(self, body: str) -> str:
        return hashlib.md5((body).encode("utf-8")).hexdigest()

    def __create_signature(
        self, check_sum: str, api_method: str, http_method: str = "POST", content_type: str = "application/json"
    ) -> str:
        now_in_RFC2822 = formatdate()
        string_to_hash = "\n".join([http_method.upper(), check_sum, content_type, now_in_RFC2822, api_method])
        return hmac.new(
            bytes(self.channel_secret, "UTF-8"), string_to_hash.encode(), digestmod=hashlib.sha1
        ).hexdigest()

    def __prepare_headers(
        self, check_sum: str, signature: str, content_type: str = "application/json"
    ) -> dict[str, str]:
        headers = {
            "Date": formatdate(),
            "Content-Type": content_type,
            "Content-MD5": check_sum.lower(),
            "X-Signature": signature.lower(),
            "User-Agent": "amocrm-py/v2",
        }

        return headers

    async def __request(self, payload: dict[str, str], api_method: str) -> httpx.Response | None:
        check_sum = self.__create_body_checksum(json.dumps(payload))
        signature = self.__create_signature(
            check_sum=check_sum,
            api_method=api_method,
        )

        headers = self.__prepare_headers(check_sum=check_sum, signature=signature)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url + api_method,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        return response

    async def _connect_channel_to_account(self) -> str:
        # get account ID in chats
        response = BaseInteraction().request("get", "account?with=amojo_id")
        account_id = response[0]["amojo_id"]

        # connect
        payload = {
            "account_id": account_id,
            "title": "ChatsIntegration",
            "hook_api_version": "v2",
        }
        response: httpx.Response = await self.__request(
            payload=payload, api_method=f"/v2/origin/custom/{self.channel_id}/connect"
        )
        return response.json()["scope_id"]

    async def create_new_chat(self, chat_id: str, contact_id: int) -> str:
        contact = Contact.objects.get(object_id=contact_id)
        payload = {
            "conversation_id": chat_id,
            "user": {
                "id": str(contact_id),
                "name": str(contact.name),
            },
        }
        response: httpx.Response = await self.__request(
            payload=payload, api_method=f"/v2/origin/custom/{self.scope_id}/chats"
        )
        return response.json()["id"]

    def connect_chat_to_contact(self, amocrm_chat_id: str, contact_id: int) -> None:
        payload = [
            {
                "contact_id": contact_id,
                "chat_id": amocrm_chat_id,
            }
        ]

        response = BaseInteraction().request(
            "post", "contacts/chats", data=payload, headers={"Content-Type": "application/json"}
        )
        if response[1] != 200:
            raise Exception("The chat could not be linked to the contact!")

    async def send_message_to_chat_as_user(self, text: str, chat_id: str, contact_id: int) -> None:
        contact = Contact.objects.get(object_id=contact_id)
        payload = {
            "event_type": "new_message",
            "payload": {
                "timestamp": int(time.time()),
                "msec_timestamp": int(time.time() * 1000),
                "msgid": str(uuid4()),
                "conversation_id": chat_id,
                "sender": {
                    "id": str(contact_id),
                    "name": str(contact.name),
                },
                "message": {
                    "type": "text",
                    "text": text,
                },
                "silent": True,
            },
        }
        await self.__request(payload=payload, api_method=f"/v2/origin/custom/{self.scope_id}")

    async def send_message_to_chat_as_bot(self, text: str, chat_id: str, contact_id: int) -> None:
        contact = Contact.objects.get(object_id=contact_id)
        payload = {
            "event_type": "new_message",
            "payload": {
                "timestamp": int(time.time()),
                "msec_timestamp": int(time.time() * 1000),
                "msgid": str(uuid4()),
                "conversation_id": chat_id,
                "sender": {
                    "id": self.bot_client_id,
                    "name": self.bot_name,
                    "ref_id": self.bot_id,
                },
                "receiver": {
                    "id": str(contact_id),
                    "name": str(contact.name),
                },
                "message": {
                    "type": "text",
                    "text": text,
                },
                "silent": True,
            },
        }
        await self.__request(payload=payload, api_method=f"/v2/origin/custom/{self.scope_id}")


async def main(chat_id: str, contact_id: int) -> None:
    amocrm_chat_id = await ChatsAPI().create_new_chat(chat_id=chat_id, contact_id=contact_id)
    ChatsAPI().connect_chat_to_contact(amocrm_chat_id=amocrm_chat_id, contact_id=contact_id)

    await ChatsAPI().send_message_to_chat_as_bot(chat_id=chat_id, text="any message", contact_id=contact_id)
    await ChatsAPI().send_message_to_chat_as_user(chat_id=chat_id, text="any message", contact_id=contact_id)


if __name__ == "__main__":
    asyncio.run(main(chat_id="1", contact_id=1))
