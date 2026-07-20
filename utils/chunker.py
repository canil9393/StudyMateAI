from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(documents):
    """
    Split extracted PDF pages into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    texts = []
    metadatas = []

    for doc in documents:
        chunks = splitter.split_text(doc["page_content"])

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "page": doc["page"],
                "source": doc["source"]
            })

    return texts, metadatas