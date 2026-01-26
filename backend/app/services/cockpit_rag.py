"""
Cockpit Client Service
This module provides functionality to interact with the Cockpit API
for processing meeting data.
"""

import requests
import uuid
import json
import os

# Configuration (Move these to .env in production)
API_ENDPOINT = "https://ibotservice.alipayplus.com/almpapi/v1/message/chat"
BOT_ID_QUERY_KB = "2026012310103009873"
BOT_ID_RESPONSE = "2026012610103024669"
BIZ_USER_ID = "Vincent Handsome Pro Max"
TOKEN_QUERY_KB = "1d4381e6-173d-426d-9d39-60199a222058"
TOKEN_RESPONSE = "d37887b5-349e-470b-b0b7-9d4fa3ab5a20"

class CockpitRAG:
    @staticmethod
    def run_workflow(input_json_string: str, workflow_type: str = "response") -> str:
        """
        Sends the meeting JSON string to Cockpit and returns the mixed-format string.
        """
        biz_request_id = str(uuid.uuid4())

        # Adjust payload based on workflow (e.g., different bot IDs if needed)
        if workflow_type == "query":
            bot_id = BOT_ID_QUERY_KB  # Example: Use a different bot ID for Workflow A if configured
            token = TOKEN_QUERY_KB
            print(f"Cockpit A - Input: {input_json_string}")
        elif workflow_type == "response":
            bot_id = BOT_ID_RESPONSE  # Or same, depending on your Cockpit setup
            token = TOKEN_RESPONSE
            print(f"Cockpit B - Input: {input_json_string}")
        else:
            raise ValueError("Invalid workflow_type. Must be 'query' or 'response'.")

        payload = {
            "botId": bot_id,
            "bizUserId": BIZ_USER_ID,
            "token": token,
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
            if workflow_type == "query":
                print(f"Cockpit A - Output: {returned_text}")
            elif workflow_type == "response":
                print(f"Cockpit B - Output: {returned_text}")
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
