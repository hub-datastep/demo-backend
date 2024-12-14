from io import BytesIO

import requests
from fastapi import HTTPException, status


def _try_download_file_partially(file_url: str):
    # Загружаем первые 512 байт файла, чтобы проверить его тип
    response = requests.get(
        url=file_url,
        stream=True,
        headers={"Range": "bytes=0-511"},
    )

    # Проверяем успешность запроса
    is_response_successful = response.status_code == 200 or response.status_code == 206
    if not is_response_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Failed to download UTD PDF file. "
                f"Status Code: {response.status_code} "
                f"Details: {response.text}"
            ),
        )

    # Проверяем, что файл является PDF по заголовкам
    content_type = response.headers.get('Content-Type', '').lower()
    is_pdf_content_type = 'pdf' in content_type
    if not is_pdf_content_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The downloaded file is not a PDF.",
        )

    # Проверяем, что файл начинается с %PDF
    is_pdf_file_valid = response.content.startswith(b'%PDF')
    if not is_pdf_file_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The downloaded file does not appear to be a valid PDF.",
        )


def download_file(file_url: str) -> BytesIO:
    # try:
    # Пробуем скачать pdf файл, чтобы провалидировать его
    _try_download_file_partially(file_url=file_url)

    # Загружаем полный файл
    response = requests.get(url=file_url)

    if not response.ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Failed to download full UTD PDF file. "
                f"Status Code: {response.status_code}"
                f"Details: {response.text}"
            ),
        )

    return BytesIO(response.content)
    # # Handle unknown errors
    # except Exception as e:
    #     error_str = str(e)
    #     logger.error(f"Error occurred while download UTD PDF file: {error_str}")
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Error occurred while download UTD PDF file: {error_str}",
    #     )


if __name__ == '__main__':
    test_file_url = 'https://ia601701.us.archive.org/10/items/atomic-habits-original/Atomic%20Habits%20Original.pdf'
    test_response = download_file(file_url=test_file_url)
    print(test_response)
