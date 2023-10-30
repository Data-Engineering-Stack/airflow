import requests
import os
from pprint import pprint


# configure :
base_url = "http://airflow.net/"
headers = {
    "Authorization": "Basic "+ os.getenv("airtoken"),
    "accept": "application/json"
}
resource_dag_list = 'api/v1/dags'


def get_data(resource,headers=None,params=None):
    try:
        # Construct the full URL
        url = f"{base_url}/{resource}"

        # Make the GET request
        response = requests.get(url,headers=headers)

        # Check for successful response (status code 200)
        if response.status_code == 200:
            pprint(response.json())
            return response.json()  
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed with error: {e}")
        return None

get_data(resource_dag_list,headers)