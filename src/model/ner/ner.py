import httpx


class HTTP_NER:
    def __init__(self, link:str="http://ner:8000/get_brands/", k:int=100, timeout:int=100):
        self.__client = httpx.Client()
        self.__k = k
        self.__timeout = timeout
        self.__link = link

    def predict(self, data:list[str]) -> list[str]:
        output = []
        for i in range(len(data)//self.__k+1):
            chunk = data[i*self.__k:i*self.__k+self.__k]
            if len(chunk) == 0:
                break
            try:
                response = self.__client.post(self.__link, json={"items": chunk}, timeout=self.__timeout)
                output.extend(response.json()['brands'])
            except Exception as e:
                print(f"Index chunk {i} - {e}")
        return output

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__client.close()

ner_model = HTTP_NER()