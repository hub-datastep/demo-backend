import re
from io import BufferedReader

from dotenv import load_dotenv
from fastapi import UploadFile
from transliterate import translit
from storage3.utils import StorageException

from dto.file_dto import StorageFileDto
from infra.supabase import supabase

load_dotenv()


BUCKET_NAME = "files"


def sanitize_filename(filename):
    sanitized_filename = str(translit(filename, "ru", reversed=True))
    sanitized_filename = sanitized_filename.replace(" ", "_")
    sanitized_filename = re.sub(r'[^a-zA-Z0-9_.]', '', sanitized_filename)
    return sanitized_filename


def get_all_files():
    res = supabase.storage.from_("files").list()
    return res


def get_file_public_url(file_path_in_bucket) -> str:
    public_url = supabase.storage.from_(
        BUCKET_NAME).get_public_url(file_path_in_bucket)
    return public_url


def upload_or_get_file(fileObject: UploadFile) -> StorageFileDto:
    try:
        file = BufferedReader(fileObject.file)
        normal_filename = sanitize_filename(fileObject.filename)

        supabase.storage \
            .from_(BUCKET_NAME) \
            .upload(
                path=normal_filename,
                file=file,
                file_options={
                    "content-type": fileObject.content_type
                }
            )
        full_file_url = get_file_public_url(normal_filename)
    except StorageException as e:
        dict_, = e.args
        if dict_["error"] == "Duplicate":
            normal_filename = sanitize_filename(fileObject.filename)
            full_file_url = get_file_public_url(normal_filename)
        else:
            raise e

    return StorageFileDto(
        filename=normal_filename,
        fileUrl=full_file_url
    )


def delete_file_from_supastorage(name_en: str):
    supabase.storage\
        .from_(BUCKET_NAME)\
        .remove([name_en])


if __name__ == "__main__":
    files = get_all_files()
    print(files[0])
    # for file in files:
    #     print(get_public_url(file["name"]))
