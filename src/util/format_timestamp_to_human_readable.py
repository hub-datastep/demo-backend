from datetime import datetime

def format_timestamp_to_human_readable(timestamp):
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)
    
    # Format the datetime object to a human-readable string
    # For "01 Jan, 03:11" format
    # human_readable_format_1 = dt_object.strftime("%d %b, %H:%M")
    
    # For "07.04.2025 15:31" format
    human_readable_format_2 = dt_object.strftime("%d.%m.%Y %H:%M")
    
    return human_readable_format_2


# if __name__ == "__main__":
#     timestamp = 1777536861  # Example timestamp
#     format_2 = format_timestamp_to_human_readable(timestamp)
#     print("Format 2:", format_2)