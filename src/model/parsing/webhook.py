import httpx

# Глобальный клиент
client = httpx.Client(timeout=10)

def kafka_request(data, link="https://example.com/api"):
    response = client.post(link, json=data)
    return response

if __name__=="__main__":
    link = "https://example.com/api"
    data = {"key": "value"}

    response_data = kafka_request(link, data)
    print(response_data)
