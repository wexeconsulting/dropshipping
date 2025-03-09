import requests

def send_get_request(url, params=None, headers=None, encoding='utf-8'):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.content.decode(response.encoding or encoding)  # Return the decoded XML content
