import sys
import time
import streamlit as st

from utils.pdf_loader import load_multiple_pdfs
from utils.chunker import create_chunks
from utils.vectorstore import create_vectorstore
from utils.rag import ask_pdf

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = None

if "texts" not in st.session_state:
    st.session_state.texts = None

if "metadatas" not in st.session_state:
    st.session_state.metadatas = None

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.title("📚 StudyMate AI")

    st.write("Upload one or more PDFs and chat with them.")

    uploaded_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    process = st.button("📄 Process PDFs")

    st.divider()

    st.info(
        """
### Supported Files

✅ PDF

(More formats coming soon...)
"""
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()
    
    st.divider()
        
    st.metric(
        "Conversation Messages",
        len(st.session_state.messages)
    )

# --------------------------------------------------
# Main Page
# --------------------------------------------------

st.title("📚 StudyMate AI")

st.caption("Chat with your PDFs using AI")

st.divider()

# --------------------------------------------------
# Uploaded PDFs
# --------------------------------------------------

if uploaded_files:

    st.subheader("Uploaded PDFs")

    for file in uploaded_files:

        st.success(file.name)

# --------------------------------------------------
# Process PDFs
# --------------------------------------------------

if process:

    if not uploaded_files:

        st.warning("Please upload at least one PDF.")

        st.stop()

    with st.spinner("Reading PDFs..."):

        documents = load_multiple_pdfs(uploaded_files)

    st.success("PDFs processed successfully!")

    total_characters = sum(
        len(doc["page_content"])
        for doc in documents
    )

    st.subheader("Document Statistics")

    st.write(f"Uploaded PDFs : {len(uploaded_files)}")
    st.write(f"Total Pages : {len(documents)}")
    st.write(f"Total Characters : {total_characters:,}")

    st.subheader("Preview")

    st.text(documents[0]["page_content"][:1200])

    # ---------------- Chunking ----------------

    texts, metadatas = create_chunks(documents)

    # ---------------- Vector Store ----------------

    with st.spinner("Creating Vector Database..."):

        vectorstore = create_vectorstore(
            texts,
            metadatas
        )

    st.session_state.documents = documents
    st.session_state.texts = texts
    st.session_state.metadatas = metadatas
    st.session_state.vectorstore = vectorstore

    st.success("✅ Vector Database Created Successfully!")

    # ---------------- Knowledge Base ----------------

    st.subheader("📚 Knowledge Base")

    pdf_names = sorted(
        list(
            {
                meta["source"]
                for meta in metadatas
            }
        )
    )

    for pdf in pdf_names:

        st.success(pdf)

    st.subheader("📦 Vector Database")

    st.write(f"Vectors Stored : {len(texts)}")

    st.subheader("Chunk Information")

    st.write(f"Total Chunks : {len(texts)}")

    st.text(texts[0][:600])

    # --------------------------------------------------
# Semantic Search
# --------------------------------------------------

if st.session_state.vectorstore is not None:

    st.divider()

    st.header("🔍 Semantic Search")

    test_query = st.text_input(
        "Search inside your PDFs",
        placeholder="Example: What is Computer Network?"
    )

    if st.button("Search"):

        if test_query.strip() == "":

            st.warning("Please enter a search query.")

        else:

            with st.spinner("Searching..."):

                docs = st.session_state.vectorstore.similarity_search(
                    test_query,
                    k=5
                )

            st.success(f"Found {len(docs)} relevant chunks")

            for i, doc in enumerate(docs, start=1):

                with st.expander(
                    f"📄 Result {i} | {doc.metadata['source']} | Page {doc.metadata['page']}"
                ):

                    st.write(doc.page_content)

# --------------------------------------------------
# Knowledge Base Summary
# --------------------------------------------------

if st.session_state.documents is not None:

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Uploaded PDFs",
            len(
                {
                    doc["source"]
                    for doc in st.session_state.documents
                }
            )
        )

    with col2:

        st.metric(
            "Pages",
            len(st.session_state.documents)
        )

    with col3:

        st.metric(
            "Chunks",
            len(st.session_state.texts)
        )

# --------------------------------------------------
# Ready Status
# --------------------------------------------------

if st.session_state.vectorstore is not None:

    st.success("🟢 StudyMate AI is ready! Ask any question below.")

    # --------------------------------------------------
# Chat Section
# --------------------------------------------------

st.divider()

st.header("💬 Chat with your PDFs")

# ---------------- Display Previous Chat ----------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and "sources" in message
        ):

            st.markdown("#### 📄 Sources")

            unique_sources = {}

            for source in message["sources"]:

                key = (
                    source["source"],
                    source["page"]
                )

                unique_sources[key] = source

            for (pdf, page), source in unique_sources.items():

                st.caption(f"📄 {pdf} | Page {page}")

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

question = st.chat_input(
    "Ask a question about your uploaded PDFs..."
)

if question:

    # ---------------- Check Vector DB ----------------

    if st.session_state.vectorstore is None:

        st.error("⚠ Please upload and process your PDFs first.")

        st.stop()

    # ---------------- User Message ----------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # ---------------- AI Response ----------------

    start_time = time.time()

    with st.spinner("🤖 Thinking..."):

        answer, docs = ask_pdf(
            st.session_state.vectorstore,
            question
        )

    end_time = time.time()

    response_time = round(
        end_time - start_time,
        2
    )

    # ---------------- Save Chat ----------------

    assistant_message = {
        "role": "assistant",
        "content": answer,
        "sources": [
            {
                "source": doc.metadata["source"],
                "page": doc.metadata["page"],
                "content": doc.page_content
            }
            for doc in docs
        ]
    }

    st.session_state.messages.append(
        assistant_message
    )

    # ---------------- Display AI ----------------

    with st.chat_message("assistant"):

        st.markdown(answer)

        st.caption(
            f"⏱ Response Time : {response_time} sec"
        )

        st.markdown("### 📄 Sources")

        unique_sources = {}

        for doc in docs:

            key = (
                doc.metadata["source"],
                doc.metadata["page"]
            )

            unique_sources[key] = doc

        for (source, page), doc in unique_sources.items():

            with st.expander(
                f"📄 {source} | Page {page}"
            ):

                st.write(doc.page_content)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "📚 StudyMate AI • Built using Streamlit, LangChain, FAISS, HuggingFace & Groq"
)