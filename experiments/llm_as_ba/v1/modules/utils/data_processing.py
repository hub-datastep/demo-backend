import csv
import json
from typing import List, Dict, Any, Optional

from llm_as_ba.v1.modules.schemas import ResidentRequest


def load_csv_data(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """Load data from a CSV file."""
    with open(file_path, 'r', encoding=encoding) as file:
        reader = csv.DictReader(file)
        return list(reader)


def load_json_data(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    with open(file_path, 'r', encoding=encoding) as file:
        return json.load(file)


def save_json_data(data: Any, file_path: str, encoding: str = 'utf-8') -> None:
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding=encoding) as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def convert_to_resident_requests(
    data: List[Dict[str, Any]],
    request_id_field: str,
    request_content_field: str,
    chat_history_field: Optional[str] = None,
) -> List[ResidentRequest]:
    """Convert raw data to ResidentRequest objects."""
    requests = []
    
    for item in data:
        request_id = item.get(request_id_field, "")
        request_content = item.get(request_content_field, "")
        
        chat_history = None
        if chat_history_field and chat_history_field in item:
            chat_history = item[chat_history_field]
        
        request = ResidentRequest(
            request_id=request_id,
            request_content=request_content,
            chat_history=chat_history,
        )
        
        requests.append(request)
    
    return requests 