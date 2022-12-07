import requests
import random
import time

url = f"https://app-sublettersapi-dev.azurewebsites.net/api/reviews/"
# url = f"http://localhost:8000/api/reviews/"



for i in range (1, 101):
    data = {
        "property_id": "f9475442-bfe7-441a-823a-39c5ea35be0c",
        "poster_id": "c4a563be-9556-4d84-acb8-b34912702626",
        "rating": random.randint(1, 5),
        "content": f"This is review {i}"
    }
    response = requests.post(url, json=data)
    print(response.text)