import os
from pypdf import PdfReader


def save_uploaded_file(uploaded_file):

    os.makedirs("temp", exist_ok=True)

    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def load_multiple_pdfs(uploaded_files):

    documents = []

    for uploaded_file in uploaded_files:

        file_path = save_uploaded_file(uploaded_file)

        reader = PdfReader(file_path)

        for page_num, page in enumerate(reader.pages):

            text = page.extract_text()

            if text:

                documents.append({
                    "page_content": text,
                    "page": page_num + 1,
                    "source": uploaded_file.name
                })

    return documents