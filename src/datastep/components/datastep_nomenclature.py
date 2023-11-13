import pathlib
import re

from infra.supabase import supabase
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rq import get_current_job
from langchain.callbacks import get_openai_callback


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


description_template = "Что такое {input}"

group_template = """Ты строитель. Ты распределяешь объекты строительства, отделки и коммуникаций по группам. Ты должен определить к какой группе относится объект.

Объект: {input}
Описание объекта: {description}

К какой группе относится объект?

Список групп:
{groups}

Используй формат:

Группа из списка:
"""

nomenclature_template = """Ты строитель. 
Ты распределяешь объекты строительства, отделки и коммуникаций по группам. 
Ты должен найти наиболее близкий к данному объект в списке. 
Ты не можешь сокращать названия объектов из списка. 

Данный объект: 
{input}

Список объектов:
{groups}

Используй формат:

Объект из списка: ответ
"""

description_prompt = PromptTemplate(
    template=description_template,
    input_variables=["input"]
)

group_prompt = PromptTemplate(
    template=group_template,
    input_variables=["input", "groups", "description"]
)

nomenclature_prompt = PromptTemplate(
    template=nomenclature_template,
    input_variables=["input", "groups"]
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

description_chain = LLMChain(llm=llm, prompt=description_prompt)
group_chain = LLMChain(llm=llm, prompt=group_prompt)
nomenclature_chain = LLMChain(llm=llm, prompt=nomenclature_prompt)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=0,
    separators=["\n"]
)


def map_with_groups(query: str, description: str, filepath: str, prev_response: str = None, index: int = None) -> str:
    groups = get_groups(filepath, prev_response[:index] if prev_response else None)

    if len(groups) == 0:
        return prev_response

    response = group_chain.run(input=query, groups=groups, description=description)
    return extract(response, "Группа из списка: (.+)")


def extract(response: str, regex: str):
    match = re.search(regex, response)
    try:
        return match.group(1)
    except:
        return response


def map_with_nomenclature(query: str, final_group: str):
    nomenclatures = get_nomenclatures(final_group)
    nomenclatures_chunks = text_splitter.split_text(nomenclatures)
    short_list = []
    for chunk in nomenclatures_chunks:
        response = nomenclature_chain.run(input=query, groups=chunk)
        nomenclature_position = extract(response, "Объект из списка: (.+)")
        short_list.append(nomenclature_position)
    groups = "\n".join(short_list)
    response = nomenclature_chain.run(input=query, groups=groups)
    return extract(response, "Объект из списка: (.+)")


def get_data_folder_path():
    return f"{pathlib.Path(__file__).parent.resolve()}"


def save_to_database(values: dict):
    return supabase.table("nomenclature_mapping").insert(values).execute()


def do_mapping(query: str) -> str:
    with get_openai_callback() as cb:
        description = description_chain.run(query)
        job = get_current_job()

        wide_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent-parent-parent.txt")
        job.meta["wide_group"] = wide_group
        job.save_meta()

        middle_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent-parent.txt", wide_group, 3)
        job.meta["middle_group"] = middle_group
        job.save_meta()

        narrow_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent.txt", middle_group, 6)
        job.meta["narrow_group"] = narrow_group
        job.save_meta()

        response = map_with_nomenclature(query, narrow_group)

        database_response = save_to_database({
            "input": query,
            "output": response,
            "wide_group": wide_group,
            "middle_group": middle_group,
            "narrow_group": narrow_group,
            "source": job.get_meta().get("source", None),
            "status": job.get_status()
        })

        job.meta["mapping_id"] = database_response.data[0]["id"]
        job.save()

    return response


if __name__ == "__main__":
    print("FINAL_RESPONSE", do_mapping("Стеклопакет 4-10-4-10-4 1149х635х32мм"))
