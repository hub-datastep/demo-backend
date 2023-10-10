import re
from io import BufferedReader

from dotenv import load_dotenv
from fastapi import UploadFile
from transliterate import translit

from dto.file_dto import StorageFileDto
from infra.supabase import supabase

load_dotenv()


BUCKET_NAME = "files"


def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[<>:\"/\\|?*]', '_', filename)
    sanitized_filename = translit(sanitized_filename, "ru", reversed=True)
    return sanitized_filename


def get_all_files():
    res = supabase.storage.from_("files").list()
    return res


def get_file_public_url(file_path_in_bucket) -> str:
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path_in_bucket)
    return public_url


def upload_file_to_supastorage(fileObject: UploadFile) -> StorageFileDto:
    file = BufferedReader(fileObject.file)
    normal_filename = sanitize_filename(fileObject.filename)

    supabase.storage\
        .from_(BUCKET_NAME)\
        .upload(
            path=normal_filename,
            file=file,
            file_options={
                "content-type": fileObject.content_type
            }
        )
    full_file_url = get_file_public_url(normal_filename)

    return StorageFileDto(
        filename=normal_filename,
        fileUrl=full_file_url
    )


if __name__ == "__main__":
    files = get_all_files()
    print(files[0])
    # for file in files:
    #     print(get_public_url(file["name"]))
