from fastapi import HTTPException
import requests
from io import BytesIO


def download_pdf(url) -> BytesIO:
    try:
        # Загружаем первые 512 байт файла, чтобы проверить его тип
        response = requests.get(url, stream=True, headers={"Range": "bytes=0-511"})
        
        # Проверяем успешность запроса
        if response.status_code != 200 and response.status_code != 206:
            raise HTTPException(status_code=400, detail=f"Failed to download file, status code: {response.status_code}")

        # Проверяем, что файл является PDF по заголовкам
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type:
            raise HTTPException(status_code=400, detail="The downloaded file is not a PDF.")

        # Проверяем, что файл начинается с %PDF
        if not response.content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="The downloaded file does not appear to be a valid PDF.")

        # Загружаем полный файл
        full_response = requests.get(url)
        if full_response.status_code == 200:
            return BytesIO(full_response.content)
        else:
            raise HTTPException(status_code=400, detail=f"Failed to download full PDF, status code: {full_response.status_code}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in function download_pdf: {str(e)}")


if __name__ == '__main__':
    print(download_pdf('https://ia601701.us.archive.org/10/items/atomic-habits-original/Atomic%20Habits%20Original.pdf'))