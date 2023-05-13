from langchain import OpenAI, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.document_loaders import FacebookChatLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from datetime import date



def construct_index(directory_path: str, openai_api_key: str):
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 128
 
    # load the messenger/instagram chats as documents
    loader = FacebookChatLoader(directory_path)

    documents = loader.load()

    # text splitting
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size_limit, chunk_overlap=max_chunk_overlap)
    texts = text_splitter.split_documents(documents)

    # Supplying a persist_directory will store the embeddings on disk
    persist_directory = './../db'

    # Embed and store the texts
    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = Chroma.from_documents(documents=texts, embedding=embedding, persist_directory=persist_directory)
    db.persist()

    return db


def ask_question(query: str, prompt_context: dict):
    name = "levi"
    date_str = date.today().strftime("%Y-%m-%d")
    date_prompt = f"Today's date is {date_str}. "
    name_prompt = f"You are speaking to someone named {prompt_context['name']}. " if prompt_context['name'] else "levi"
    prompt_template = (
            date_prompt
            + name_prompt
            + (
                """Use the following pieces of chat messages to either answer the question below or infer based on the context. If you don't know the answer, just say that you don't know, don't try to make up an answer. 

                {context}

                "Question: {question}
                "Answer:"""
            )
        )
    # """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    # {context}

    # Question: {question}
    # Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    persist_directory = './../db'
    embedding = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding)

    chain_type_kwargs = {"prompt": PROMPT, "verbose": True}

    qa = RetrievalQA.from_chain_type(llm=OpenAI(),
                                     chain_type="stuff",
                                     chain_type_kwargs=chain_type_kwargs,
                                     retriever=vectorstore.as_retriever())

    response = qa({"query": query})
    return response['result']