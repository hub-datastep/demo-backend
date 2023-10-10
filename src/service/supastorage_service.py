from infra.supabase import supabase


def get_all_files():
    res = supabase.storage.from_("files").list()
    return res


def get_public_url(filename: str) -> str:
    return supabase.storage.from_("files").get_public_url(filename)


if __name__ == "__main__":
    files = get_all_files()
    print(files[0])
    # for file in files:
    #     print(get_public_url(file["name"]))
