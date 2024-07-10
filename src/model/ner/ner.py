import httpx

# class HTTP_NER:
#     def __init__(self, link:str, k:int=100, timeout:int=100):
#         self.__client = httpx.AsyncClient()
#         self.__k = k
#         self.__timeout = timeout
#         self.__link = link

#     async def predict(self, data:list[str]) -> list[str]:
#         output = []
#         for i in range(len(data)//self.__k+1):
#             chunk = data[i*self.__k:i*self.__k+self.__k]
#             if len(chunk) == 0:
#                 break
#             try:
#                 response = await self.__client.post(self.__link, json={"items": chunk}, timeout=self.__timeout)
#                 output.extend(response.json()['brands'])
#             except Exception as e:
#                 print(f"Index chunk {i} - {e}")
#         return output

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self.__client.aclose()


class HTTP_NER:
    def __init__(self, link:str="http://ner:8000/get-brands/", k:int=100, timeout:int=100):
        self.__client = httpx.Client()  # Изменено на синхронный клиент
        self.__k = k
        self.__timeout = timeout
        self.__link = link

    def predict(self, data:list[str]) -> list[str]:  # Изменено на синхронный метод
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

    def __exit__(self, exc_type, exc_val, exc_tb):  # Изменено на синхронный метод
        self.__client.close()

ner_model = HTTP_NER()