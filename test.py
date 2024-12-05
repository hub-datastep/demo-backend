import requests
import uuid
from datetime import datetime

def generate_uuid():
    """Generates a random UUID4 string."""
    return str(uuid.uuid4())

def get_current_iso_datetime():
    """Returns the current UTC datetime in ISO 8601 format."""
    return datetime.utcnow().isoformat()

def create_upload_card_request():
    """Creates the payload for the UploadCardRequest."""
    return {
        "guid": generate_uuid(),
        "idn_datetime": get_current_iso_datetime(),
        "responsible_user_email": "user@example.com",  # Replace with actual email if needed
        "operation_kind": "example_operation",         # Replace with actual operation kind
        "building_guid": generate_uuid(),
        "contractor_guid": generate_uuid(),
        "documents": [
            {
                "idn_file_guid": generate_uuid(),
                "idn_link": "https://ia601701.us.archive.org/10/items/atomic-habits-original/Atomic%20Habits%20Original.pdf",
                "idn_file_name": "Atomic_Habits_Original.pdf"
            }
        ]
    }

def send_post_request(url, payload):
    """Sends a POST request to the specified URL with the given payload."""
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6+
        print(f"Response content: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6+
    return None

def main():
    # Define the server URL
    # If you're using versioning and your endpoint is prefixed with the version (e.g., /v1/parsing), adjust accordingly.
    url = "http://localhost:8080/parsing"

    # Create the payload
    payload = create_upload_card_request()

    # Display the payload for debugging purposes
    print("Sending the following payload:")
    print(payload)

    # Send the POST request
    print(f"\nSending POST request to {url}...")
    response = send_post_request(url, payload)

    # Handle the response
    if response:
        print("\nRequest was successful. Response JSON:")
        print(response)
    else:
        print("\nRequest failed.")

if __name__ == "__main__":
    main()
