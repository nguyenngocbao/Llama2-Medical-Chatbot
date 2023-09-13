from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
import pinecone

PINECONE_API_KEY = ''
PINECONE_ENV = ''
PINECONE_INDEX_NAME = ''

# Create vector database
def create_vector_db():
    loader = DirectoryLoader(DATA_PATH,
                             glob='*.pdf',
                             loader_cls=PyPDFLoader)

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                       model_kwargs={'device': 'cpu'})

    # initialize pinecone
    pinecone.init(
      api_key= PINECONE_API_KEY,  # find at app.pinecone.io
      environment= PINECONE_ENV,  # next to api key in console
    )

    index_name = PINECONE_INDEX_NAME

    if index_name not in pinecone.list_indexes():
    # we create a new index
        pinecone.create_index(
        name=index_name,
        metric='cosine',
        dimension=384  
    )

    db = Pinecone.from_documents(texts, embeddings, index_name=index_name)

if __name__ == "__main__":
    create_vector_db()

