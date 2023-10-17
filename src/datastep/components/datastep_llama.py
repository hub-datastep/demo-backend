import pathlib

from llama_index import VectorStoreIndex, download_loader, StorageContext, load_index_from_storage, ServiceContext

def get_storage_path(source_id):
    return f"{pathlib.Path(__file__).parent.resolve()}/../../../llama/data/{source_id}"


def save_document(source_id: str, file_url: str):
    RemoteReader = download_loader("RemoteReader")
    loader = RemoteReader()
    documents = loader.load_data(url=file_url)
    service_context = ServiceContext.from_defaults(chunk_size=256)
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    index.storage_context.persist(persist_dir=get_storage_path(source_id))


def query(source_id: str, query: str):
    storage_context = StorageContext.from_defaults(persist_dir=get_storage_path(source_id))
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(similarity_top_k=10)
    response = query_engine.query(query)
    # source_nodes_sorted_by_score = sorted(
    #     response.source_nodes,
    #     key=lambda n: n.get_score(),
    #     reverse=True
    # )
    for node in response.source_nodes:
        print(node.get_score())
        print(node.get_content())
        print()
    return response.source_nodes[0].metadata["page_label"], str(response)


if __name__ == "__main__":
    pass
    # persist()
    # response = search("Характеристики смесителя")
    # print(response)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(response.source_nodes)
    #
    # response = response.get_formatted_sources()
    # print(response)
