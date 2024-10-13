from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from model.preprocessing import clean
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA

def get_page_content(docs):
    data=[]
    for index in range(len(docs)):
        doc=clean(docs[index].page_content)
        data.append(doc)
    return data

def load_dataset():
    folder_path = r'documents'
    mixed_loader = DirectoryLoader(
        path=folder_path,
        glob='*.pdf',
        loader_cls=PyPDFLoader  
    )
    docs = mixed_loader.load()
    docs=get_page_content(docs)
    return docs

def split_documents_into_chunks():
     docs=load_dataset()
     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
     chunks= text_splitter.split_documents(docs)
     return chunks

def store_index_chunks():
     chunks=split_documents_into_chunks()
     encoder = HuggingFaceEmbeddings()
     db = FAISS.from_documents(documents=chunks, embedding=encoder)
     retriever = db.as_retriever(search_kwargs={"k": 10})
     return retriever

def load_llm():
     model_name="google/gemma-1.1-7b-it"
     token="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"
     quantization_config = BitsAndBytesConfig(load_in_4bit=True)
     model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=token, quantization_config=quantization_config)
     tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=token, quantization_config=quantization_config)
     return model,tokenizer


def retrive_relevant_documents():
   model,tokenizer=load_llm()
   retriever=store_index_chunks()
   pipe = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=150,model_kwargs={"temperature": 0.7}
    )
   hf = HuggingFacePipeline(pipeline=pipe)
   qa = RetrievalQA.from_chain_type(llm=hf, retriever=retriever, chain_type="stuff")
   return qa

def get_answer(query:str):
    qa=retrive_relevant_documents()
    answer = qa.run(query)
    return answer


