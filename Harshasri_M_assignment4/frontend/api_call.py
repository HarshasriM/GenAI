import requests

def get_response(conversational_id,query):
    url = "http://localhost:8000/query"
    payload = {"conversational_id":conversational_id,"query":query}
    try:
        response = requests.post(url,json=payload)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.exceptions.HTTPError as err:
        return {"conversational_id":None,"response":"Sorry, I am not able to process your request at the moment. Please try again later."}