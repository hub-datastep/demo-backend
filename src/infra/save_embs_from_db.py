from pandas import DataFrame

from infra.chroma_embeddings import save_nom_embeddings


def get_noms() -> DataFrame:
    # noms = read_sql(
    #     'SELECT * FROM nomenclature WHERE embeddings IS NOT NULL',
    #     os.getenv("DB_CONNECTION_STRING")
    # )
    noms = DataFrame([
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
        {
            "nomenclature": "1",
            "group": "2",
            "embeddings": "3",
        },
    ])
    return noms


if __name__ == "__main__":
    noms = get_noms()
    save_nom_embeddings(
        ids=noms.index,
        nomenclatures=noms.nomenclature,
        groups=noms.group,
        embeddings=noms.embeddings
    )
    pass
