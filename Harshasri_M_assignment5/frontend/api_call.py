import requests

def get_response(conversational_id, query):
    url = "http://localhost:8000/query"
    payload = {
        "conversational_id": conversational_id,
        "query": query
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def generate_vector_database(conversational_id, filename):
    url = "http://localhost:8000/create/vector/database"
    payload = {
        "conversational_id": conversational_id,
        "filename": filename
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        return e
