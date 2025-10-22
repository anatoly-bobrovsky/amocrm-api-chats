# Integration with AmoCRM Chat API in Python

This repository demonstrates how to integrate the [amoCRM](https://www.amocrm.com/) chat API using Python. The project adapts the amoCRM documentation from PHP to Python, providing a practical implementation for developers.

Note: the `docs/` folder contains an additional article provided in both Russian and English.

## Prerequisites

1. A working amoCRM account.
2. Familiarity with the [amoCRM chat API documentation](https://www.amocrm.com/developers/content/chats/chat-start).
3. A public server with an SSL certificate for the Webhook URL.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anatoly-bobrovsky/amocrm-api-chats.git
   cd amocrm-api-chats
   ```

2. Install dependencies:
   ```bash
   pip install -r src/process_from_amocrm/requirements.txt

   or

   pip install -r src/send_to_amocrm/requirements.txt
   ```

3. Configure environment variables with `env_settings.py` files.

## Usage

1. **Connect Channel to Account**  
    Call `_connect_channel_to_account` method and write `scope_id` to environment variables.

2. **Create Chat**  
     ```python
    amocrm_chat_id = await ChatsAPI().create_new_chat(chat_id=chat_id, contact_id=contact_id)
    ChatsAPI().connect_chat_to_contact(amocrm_chat_id=amocrm_chat_id, contact_id=contact_id)
     ```

3. **Send Messages**  
   - As a bot: 
     ```python
     await ChatsAPI().send_message_to_chat_as_bot(chat_id="chat_id", text="message", contact_id=contact_id)
     ```
   - As a user:
     ```python
     await ChatsAPI().send_message_to_chat_as_user(chat_id="chat_id", text="message", contact_id=contact_id)
     ```

4. **Process Messages**  
   Deploy the `FastAPI` server to handle incoming messages from amoCRM:
   ```bash
   python src/process_from_amocrm/api_app.py
   ```

