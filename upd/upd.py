import pdfplumber
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Проверка на тип файла
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Загружаемый файл должен быть в формате PDF.")
    
    try:
        # Используем file.file (это файловый объект) для обработки в pdfplumber
        with pdfplumber.open(file.file) as pdf:
            # Извлекаем текст со всех страниц
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        return {
            "filename": file.filename,
            "content": text.strip()  # Возвращаем извлечённый текст
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке PDF: {str(e)}")
