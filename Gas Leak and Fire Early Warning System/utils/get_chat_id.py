import requests

token = "8400886945:AAF0aQlTCgxRWqAPPFLQ_2PeW8JL5foh7H4"
r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
print(r.json())  # lihat response, ambil response['result'][0]['message']['chat']['id']

r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
group_ids = [
    item["message"]["chat"]["id"]
    for item in r.get("result", [])
    if item["message"]["chat"]["type"] != "private"
]
print(group_ids)
