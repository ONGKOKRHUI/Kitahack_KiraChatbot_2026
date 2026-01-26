"""
handles parsing of cockpit output into structured data.
"""

import re
import json
from datetime import datetime

class CockpitParser:
    def __init__(self):
        # Regex patterns to identify the start of each section
        self.patterns = {
            "decisions": r"final_decision:",
            "summary": r"final_meeting_sum:",
            "actions": r"final_actions:"
        }

    def parse(self, raw_text: str) -> dict:
        """
        Splits the raw string into 3 structured chunks with metadata.
        """
        parsed_data = {
            "decisions": {"metadata": {}, "content": []},
            "summary": {"metadata": {}, "content": []},
            "actions": {"metadata": {}, "content": []}
        }

        # 1. Split the text by the known headers
        # We capture the delimiter to know which section we are in
        split_pattern = f"({'|'.join(self.patterns.values())})"
        tokens = re.split(split_pattern, raw_text)

        current_section_key = None

        for token in tokens:
            token = token.strip()
            
            # Check if this token is a header (e.g., "final_decision:")
            found_header = False
            for key, header in self.patterns.items():
                if token == header:
                    current_section_key = key
                    found_header = True
                    break
            
            if found_header:
                continue

            # If it's not a header and we have a section active, this is the content
            if current_section_key and token:
                # 2. Extract Metadata (e.g., [Meeting: A100...])
                metadata_match = re.search(r"\[(Meeting:.*?\|.*?)\]", token)
                if metadata_match:
                    raw_meta = metadata_match.group(1)
                    parsed_data[current_section_key]["metadata"] = self._parse_metadata(raw_meta)
                
                # 3. Extract JSON "result" content
                # We extract the JSON objects to get the clean text inside "result"
                # If you prefer the raw string, we can skip this and just save 'token'
                json_matches = re.findall(r'(\{.*?\})(?=\{|$)', token, re.DOTALL)
                clean_content = []
                for j_str in json_matches:
                    try:
                        data = json.loads(j_str)
                        if "result" in data and data["result"].strip():
                            clean_content.append(data["result"])
                    except json.JSONDecodeError:
                        continue
                
                parsed_data[current_section_key]["content"] = clean_content

        return parsed_data

    def _parse_metadata(self, meta_string: str) -> dict:
        """
        Converts 'Meeting: A100 | Date: 1-Jan' into {'Meeting': 'A100', 'Date': '1-Jan'}
        """
        meta_dict = {}
        parts = meta_string.split("|")
        for part in parts:
            if ":" in part:
                key, val = part.split(":", 1)
                meta_dict[key.strip()] = val.strip()
        return meta_dict


    # def _parse_metadata(self, meta_string: str) -> dict:
    #     """
    #     Converts 'Meeting: A100 | Date: 1-Jan-2026' into 
    #     {'Meeting': 'A100', 'Date': datetime(2026, 1, 1)}
    #     """
    #     meta_dict = {}
    #     parts = meta_string.split("|")
    #     for part in parts:
    #         if ":" in part:
    #             key, val = part.split(":", 1)
    #             key = key.strip()
    #             val = val.strip()
                
    #             # Convert Date string to datetime object if possible
    #             if key.lower() == "date":
    #                 try:
    #                     # Try parsing full date first
    #                     meta_dict[key] = datetime.strptime(val, "%d-%b-%Y")
    #                 except ValueError:
    #                     # Fallback: just day-month (assume current year)
    #                     try:
    #                         current_year = datetime.now().year
    #                         meta_dict[key] = datetime.strptime(f"{val}-{current_year}", "%d-%b-%Y")
    #                     except ValueError:
    #                         # If parsing fails, leave as string
    #                         meta_dict[key] = val
    #             else:
    #                 meta_dict[key] = val
    #     return meta_dict

"""
Output JSON format:

{
  "decisions": {
    "metadata": {
      "Meeting": "A100",
      "Date": "1-Jan"
    },
    "content": [
      "Approve project X",
      "Notify stakeholders"
    ]
  },
  "summary": {
    "metadata": {
      "Meeting": "A100",
      "Date": "1-Jan"
    },
    "content": [
      "Meeting went smoothly, tasks defined."
    ]
  },
  "actions": {
    "metadata": {},
    "content": [
      "Assign task A to John",
      "Follow up with vendor"
    ]
  }
}
"""