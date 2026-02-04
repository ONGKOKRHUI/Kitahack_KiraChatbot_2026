"""
Cockpit Client Service
This module provides functionality to interact with the Cockpit API
for processing meeting data.
triggered by Graph API 
"""

import requests
import uuid
import json
import os

# Configuration (Move these to .env in production)
API_ENDPOINT = "https://ibotservice.alipayplus.com/almpapi/v1/message/chat"
BOT_ID = "2026011610102948943"
BIZ_USER_ID = "Vincent Handsome"
TOKEN = "ecd8be0c-cd53-4861-89d5-12f34c11d295"

class CockpitClient:
    @staticmethod
    def run_workflow(input_json_string: str) -> str:
        """
        Sends the meeting JSON string to Cockpit and returns the mixed-format string.
        """
        biz_request_id = str(uuid.uuid4())
        
        payload = {
            "botId": BOT_ID,
            "bizUserId": BIZ_USER_ID,
            "token": TOKEN,
            "stream": False,
            "bizRequestId": biz_request_id,
            "chatContent": {
                "contentType": "TEXT",
                "text": input_json_string
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(API_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            api_response = response.json()
            
            # Safe extraction with checks to avoid IndexError
            data = api_response.get('data', {})
            message_list = data.get('messageList', [])
            if not message_list:
                raise ValueError("Cockpit API returned empty messageList")
            first_message = message_list[0]
            content = first_message.get('content', [])
            if not content:
                raise ValueError("Cockpit API returned empty content in messageList[0]")
            returned_text = content[0].get('text', 'No text found in response')
            return returned_text
            
        except requests.exceptions.RequestException as e:
            print(f"Cockpit API Request Error: {e}")
            raise ValueError(f"Cockpit API request failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            print(f"Cockpit API Parsing Error: {e}")
            raise ValueError(f"Cockpit API response parsing failed: {str(e)}")
        except Exception as e:
            print(f"Cockpit API Unexpected Error: {e}")
            raise e


#### OLD CODE FOR TESTING PURPOSES ONLY ####        
"""
import requests
import json
import uuid
import os

# --- Configuration ---
API_ENDPOINT = "https://ibotservice.alipayplus.com/almpapi/v1/message/chat"
BOT_ID = "2026011610102948943"
BIZ_USER_ID = "xxx"
TOKEN = "ecd8be0c-cd53-4861-89d5-12f34c11d295"

# ---------------------
def generate_api_payload(markdown_text: str):
    biz_request_id = str(uuid.uuid4())
    payload = {
        "botId": BOT_ID,
        "bizUserId": BIZ_USER_ID,
        "token": TOKEN,
        "stream": False,
        "bizRequestId": biz_request_id,
        "chatContent": {
            "contentType": "TEXT",
            "text": markdown_text
        }
    }
    return payload, biz_request_id

def extract_boolean_result(api_response: dict):
    # Extract the boolean result from the API response
    # try:
    #     text_value = (
    #         api_response
    #         .get("data", {})
    #         .get("messageList", [{}])[0]
    #         .get("content", [{}])[0]
    #         .get("text", "")
    #     )
    #     # Clean formatting: backticks, whitespace, newline
    #     cleaned = text_value.replace("`", "").strip().lower()
    #     if cleaned == "true":
    #         return True
    #     if cleaned == "false":
    #         return False
    #     return None
    # except (IndexError, AttributeError):
    #     return None
    pass


def test_api_with_markdown(markdown_text: str):
    payload, request_id = generate_api_payload(markdown_text)
    headers = {"Content-Type": "application/json"}
    print("bizRequestId:", request_id)
    print("Sending request...\n")
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    api_response = response.json()
    #result = extract_boolean_result(api_response)
    # print("\nParsed Boolean Result:", result)
    # return result
    print("API Response:\n", json.dumps(api_response, indent=2))

    #export response to JSON file
    # with open("data/api_response.json", "w", encoding="utf-8") as f:
    #     json.dump(api_response, f, ensure_ascii=False, indent=2)

    #print(f"\nAPI response saved to 'data/api_response.json'")
    returned_text = api_response['data']['messageList'][0]['content'][0]['text']
    print("\nReturned Text:\n", returned_text)


if __name__ == "__main__":
    TXT_PATH = "/Users/001982/Documents/repo/tng-info-intelligence/workflow/0.0.complete_input"
    with open(TXT_PATH, 'r', encoding='utf-8') as file:
        data = file.read()
    test_api_with_markdown(data)
"""