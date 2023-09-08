from datetime import datetime

def _parse_timestamp_to_date(timestamp:str) -> datetime:
    """
    Parse a timestamp string to a datetime object
    """
    return datetime.strptime(timestamp, r'%Y-%m-%dT%H:%M:%SZ')