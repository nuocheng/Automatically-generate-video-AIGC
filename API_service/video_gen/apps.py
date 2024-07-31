from django.apps import AppConfig
from django.conf import settings
import os
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
import pandas as pd

class VideoGenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_gen'

    def ready(self):
        settings.font_path = "/home/zhangcd/video_serve/API_service/static/font/STKaiti/STKaiti.ttf"
        embedding_model = "/mnt/nodestor/cluster_share_folder/user-fs/train/zcd/embedding_model/multilingual-e5-large-instruct"
        db_vector_path = os.path.join(settings.BASE_DIR, "static", "vector_data_embedding")
        data_path = os.path.join(settings.BASE_DIR, "static", "data")
        demo_data = os.path.join(settings.BASE_DIR, "static", "data","image_content.csv")

        loader = DirectoryLoader(data_path, "**/*.csv", show_progress=True, use_multithreading=True,
                                 loader_cls=TextLoader)

        loader = CSVLoader(demo_data)
        document = loader.load()
        # texts_splitter = CharacterTextSplitter()
        # texts = texts_splitter.split_documents(document)
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        if os.path.exists(db_vector_path):
            db = FAISS.load_local(db_vector_path, embeddings, allow_dangerous_deserialization=True)
        else:
            db = FAISS.from_documents(document, embeddings)
            # db = Chroma(embedding_function=embeddings, persist_directory=db_vector_path)
            db.save_local(db_vector_path)

        settings.db = db.as_retriever(search_type="similarity_score_threshold",
                                      search_kwargs={"score_threshold": .1, "k": 5})

        settings.demo_data = pd.read_csv(demo_data)
        settings.ip_config = "http://10.40.0.196:18091"