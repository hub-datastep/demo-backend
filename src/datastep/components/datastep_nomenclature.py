import pathlib
import re

from infra.supabase import supabase
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rq import get_current_job


def get_nomenclatures(group: str) -> str:
    response = supabase \
        .table("nomenclature") \
        .select("Номенклатура") \
        .eq("Группа", group) \
        .execute()
    return "\n".join([d["Номенклатура"] for d in response.data])


def get_groups(filepath: str, group_number: str = None) -> str:
    with open(filepath, "r") as f:
        lines = f.readlines()
        if group_number:
            lines = [line for line in lines if line.startswith(group_number)]
        return "".join(lines)


group_template = """Ты системный аналитик. Ты знаешь SQL, системный анализ и бизнес-анализ. Ты умеешь находить схожие материалы из предоставленного списка.
Ты должен определить к какой группе относится {input}

Список групп:
{groups}

Покажи только название группы с номером
"""

nomenclature_template = """Ты системный аналитик. Ты знаешь SQL, системный анализ и бизнес-анализ. Ты умеешь находить схожие материалы из предоставленного списка.
Cопоставь данную позицию с позицией из списка. 

Данная позиция: 
{input}

Список позиций:
{groups}

Используй формат

Данная позиция:
Позиция из списка:
"""

group_prompt = PromptTemplate(
    template=group_template,
    input_variables=["input", "groups"]
)

nomenclature_prompt = PromptTemplate(
    template=nomenclature_template,
    input_variables=["input", "groups"]
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

group_chain = LLMChain(llm=llm, prompt=group_prompt)
nomenclature_chain = LLMChain(llm=llm, prompt=nomenclature_prompt)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=0,
    separators=["\n"]
)


def map_with_groups(query: str, filepath: str, prev_response: str = None, index: int = None) -> str:
    groups = get_groups(filepath, prev_response[:index] if prev_response else None)

    if len(groups) == 0:
        return prev_response

    return group_chain.run(input=query, groups=groups)


def extract_nomenclature(response: str):
    match = re.search("Позиция из списка: (.+)", response)
    return match.group(1)


def map_with_nomenclature(query: str, final_group: str):
    nomenclatures = get_nomenclatures(final_group)
    nomenclatures_chunks = text_splitter.split_text(nomenclatures)
    short_list = []
    for chunk in nomenclatures_chunks:
        response = nomenclature_chain.run(input=query, groups=chunk)
        nomenclature_position = extract_nomenclature(response)
        short_list.append(nomenclature_position)
    groups = "\n".join(short_list)
    response = nomenclature_chain.run(input=query, groups=groups)
    return extract_nomenclature(response)


def get_data_folder_path():
    return f"{pathlib.Path(__file__).parent.resolve()}"


def save_to_database(values: dict):
    return supabase.table("nomenclature_mapping").insert(values).execute()


def do_mapping(query: str) -> str:
    job = get_current_job()

    wide_group = map_with_groups(query, f"{get_data_folder_path()}/../data/parent-parent-parent.txt")
    job.meta["wide_group"] = wide_group
    job.save_meta()

    middle_group = map_with_groups(query, f"{get_data_folder_path()}/../data/parent-parent.txt", wide_group, 3)
    job.meta["middle_group"] = middle_group
    job.save_meta()

    narrow_group = map_with_groups(query, f"{get_data_folder_path()}/../data/parent.txt", middle_group, 6)
    job.meta["narrow_group"] = narrow_group
    job.save_meta()

    response = map_with_nomenclature(query, narrow_group)

    database_response = save_to_database({
        "input": query,
        "output": response,
        "wide_group": wide_group,
        "middle_group": middle_group,
        "narrow_group": narrow_group,
        "source": job.get_meta().get("source", None)
    })

    job.meta["mapping_id"] = database_response.data[0]["id"]
    job.save()

    return response


if __name__ == "__main__":
    pass
