from pathlib import Path

# Файл или папка, который, если найдётся в древе, то поиск остановится
SEARCH_LIMIT_TARGET = "src"


def _raise_file_not_found_exception(
    file_or_dir_name: str,
    current_path: str | Path,
) -> FileNotFoundError:
    current_path = str(current_path)
    return FileNotFoundError(
        f"File or Dir '{file_or_dir_name}' not found in '{current_path}'"
    )


def find_path_to_file_or_dir(file_or_dir_name: str) -> str:
    current_file_path = Path(__file__).resolve()

    # Текущая директория скрипта
    current_path = current_file_path.parent

    # Пока не достигнем корневой директории
    while current_path != current_path.parent:
        # Путь к искомому файлу
        file_path = current_path / file_or_dir_name

        is_file_exists = file_path.exists()
        if is_file_exists:
            return str(file_path)

        if (current_path / SEARCH_LIMIT_TARGET).exists() and not is_file_exists:
            raise _raise_file_not_found_exception(
                file_or_dir_name=file_or_dir_name,
                current_path=current_path,
            )

        # Поднимаемся на уровень выше
        current_path = current_path.parent

    raise _raise_file_not_found_exception(
        file_or_dir_name=file_or_dir_name,
        current_path=current_path,
    )
