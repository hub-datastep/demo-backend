import pathlib
import re

from infra.supabase import supabase
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rq import get_current_job
from langchain.callbacks import get_openai_callback
from langchain.chains.openai_functions import create_structured_output_runnable


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

group_template = """"Для объекта выбери строго одну подходящую категорию из списка.
Учти описание объекта.

Объект: {input}
Описание объекта: {description}

Категории:
{groups}
"""

nomenclature_template = """Найди в списке такой же объект.
Если в списке нет такого же объекта, напиши 0

Объект: 
{input}

Список:
{groups}
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

gpt_3 = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106", max_retries=3, request_timeout=10)
gpt_4 = ChatOpenAI(temperature=0, model_name="gpt-4-1106-preview", max_retries=3, request_timeout=10)

group_json_schema = {
    "title": "category",
    "description": "category from list",
    "type": "object",
    "properties": {
        "category": {"title": "category", "description": "category number and name", "type": "string"},
    },
    "required": ["category"],
}

nomenclature_json_schema = {
    "title": "object",
    "description": "object from list",
    "type": "object",
    "properties": {
        "nomenclature": {"title": "object_name", "description": "object name or 0", "type": "string"},
    },
    "required": ["nomenclature"],
}


group_runnable_gpt_3 = create_structured_output_runnable(group_json_schema, gpt_3, group_prompt)
group_runnable_gpt_4 = create_structured_output_runnable(group_json_schema, gpt_4, group_prompt)
nomenclature_runnable = create_structured_output_runnable(nomenclature_json_schema, gpt_4, nomenclature_prompt)

description_chain = LLMChain(llm=gpt_3, prompt=description_prompt)
# group_chain = LLMChain(llm=llm, prompt=group_prompt)
# nomenclature_chain = LLMChain(llm=llm, prompt=nomenclature_prompt)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=0,
    separators=["\n"]
)


def map_with_groups(query: str, description: str, filepath: str, group_runnable, prev_response: str = None, index: int = None) -> str:
    groups = get_groups(filepath, prev_response[:index] if prev_response else None)

    if len(groups) == 0:
        return prev_response

    response = group_runnable.invoke({"input": query, "groups": groups, "description": description})
    return response["category"]


def extract(response: dict, regex: str):
    return response["category"]
    # match = re.search(regex, response)
    # try:
    #     return match.group(1)
    # except:
    #     return response


def map_with_nomenclature(query: str, final_group: str):
    nomenclatures = get_nomenclatures(final_group)
    nomenclatures_chunks = text_splitter.split_text(nomenclatures)
    short_list = []
    for chunk in nomenclatures_chunks:
        response = nomenclature_runnable.invoke({"input": query, "groups": chunk})
        nomenclature_position = response["nomenclature"]
        short_list.append(nomenclature_position)
    groups = "\n".join(str(short_list))
    response = nomenclature_runnable.invoke({"input": query, "groups": groups})
    return response["nomenclature"]


def get_data_folder_path():
    return f"{pathlib.Path(__file__).parent.resolve()}"


def save_to_database(values: dict):
    return supabase.table("nomenclature_mapping").insert(values).execute()


def do_mapping(query: str) -> str:
    with get_openai_callback() as cb:
        description = description_chain.run(query)
        # print(description)
        job = get_current_job()

        # wide_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent-parent-parent.txt", group_runnable_gpt_4)
        # print(wide_group)
        # job.meta["wide_group"] = wide_group
        # job.save_meta()

        middle_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent-parent.txt", group_runnable_gpt_3)
        # print(middle_group)
        job.meta["middle_group"] = middle_group
        job.save_meta()

        narrow_group = map_with_groups(query, description, f"{get_data_folder_path()}/../data/parent.txt", group_runnable_gpt_3, middle_group, 6)
        # print(narrow_group)
        job.meta["narrow_group"] = narrow_group
        job.save_meta()

        response = map_with_nomenclature(query, narrow_group)

        database_response = save_to_database({
            "input": query,
            "output": response,
            "wide_group": "",
            "middle_group": middle_group,
            "narrow_group": narrow_group,
            "source": job.get_meta().get("source", None),
            "status": job.get_status()
        })

        job.meta["mapping_id"] = database_response.data[0]["id"]
        job.save()

    # print("$" + str(cb.prompt_tokens * 0.01 / 1000 * cb.completion_tokens * 0.03 / 1000))

    return response


if __name__ == "__main__":
    print("FINAL_RESPONSE", do_mapping("Полка под принтер к теплосчётчику ВИС.Т"))
