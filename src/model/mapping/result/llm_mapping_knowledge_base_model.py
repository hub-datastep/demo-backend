from numpy import nan
from pandas import DataFrame

from infra.chroma_store import add_embeddings, connect_to_chroma_collection
from scheme.mapping.llm_mapping_scheme import LLMMappingResult
from scheme.mapping.result.mapping_result_scheme import MappingResult, CorrectedResult
from util.uuid import generate_uuid

# Knowledge Base vectorstore collection name
UNISTROY_KB_COLLECTION_NAME = "unistroy_knowledge_base"


def save_to_knowledge_base(
    mapping_result: MappingResult,
) -> dict:
    result = LLMMappingResult(**mapping_result.result)

    # Extract predicted nomenclature
    predicted_nomenclature_name: str | None = None
    if result.mappings:
        predicted_nomenclature_name = result.mappings[0].nomenclature.strip()

    # Extract feedback, correct nomenclature
    correct_nomenclature_name: str | None = None
    feedback: str | None = None
    corrected_result = mapping_result.corrected_nomenclature
    if corrected_result:
        # Extract feedback
        corrected_result = CorrectedResult(
            **mapping_result.corrected_nomenclature,
        )
        feedback = corrected_result.feedback

        # Extract correct nomenclature
        if corrected_result.nomenclature:
            correct_nomenclature_name = corrected_result.nomenclature.name.strip()

    # Check if result is correct
    is_correct = predicted_nomenclature_name == correct_nomenclature_name

    # Combine new knowledge
    new_knowledge = {
        "id": f"{generate_uuid()}",
        "УПД материал": result.nomenclature,
        "Класс УПД материала": result.group,
        "Предсказанный НСИ материал": predicted_nomenclature_name,
        "Правильный материал НСИ": correct_nomenclature_name,
        "Фидбек Оператора": feedback,
        "Правильное предсказание?": is_correct,
        "ID итерации сопоставления": mapping_result.iteration_id,
    }
    new_knowledge_df = DataFrame([new_knowledge])

    # Prepare params to save in Knowledge Base
    ids = new_knowledge_df["id"].to_list()
    documents = new_knowledge_df["УПД материал"].to_list()
    metadatas = (
        new_knowledge_df.drop(
            columns=[
                "id",
                "УПД материал",
            ],
        )
        .fillna(value=nan)
        .to_dict(orient="records")
    )

    # Connect to Knowledge Base vectorstore collection
    collection = connect_to_chroma_collection(
        collection_name=UNISTROY_KB_COLLECTION_NAME,
    )
    # Save to knowledge base
    add_embeddings(
        collection=collection,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return new_knowledge
