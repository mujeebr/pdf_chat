import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
import config

api_key = config.api_key

secret=config.secret
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.secret_key = secret  # Your random secret key

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('process_file', filename=file.filename))
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    logger.info(f"Processing file: {filepath}")

    try:
        # Load PDF and process it
        loader = PyPDFDirectoryLoader(app.config['UPLOAD_FOLDER'])
        data = loader.load()
        logger.info(f"Data loaded: {data}")

        if not data:
            flash('No content extracted from the PDF')
            return redirect(url_for('index'))

        # Create text chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(data)
        logger.info(f"Text chunks: {text_chunks}")

        if not text_chunks:
            flash('No text chunks created')
            return redirect(url_for('index'))

        # Generate embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Create FAISS vector store
        vectorstore = FAISS.from_documents(text_chunks, embeddings)

        # Initialize OpenAI LLM
        llm = OpenAI(api_key=api_key)

        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

        return render_template('result.html', filename=filename)

    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        flash('An error occurred while processing the PDF')
        return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form['question']
    filename = request.form['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Load PDF and process it again (you might want to cache this for efficiency)
        loader = PyPDFDirectoryLoader(app.config['UPLOAD_FOLDER'])
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(data)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(text_chunks, embeddings)
        llm = OpenAI(api_key=api_key)
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

        answer = qa.run(question)
        return render_template('result.html', filename=filename, question=question, answer=answer)

    except Exception as e:
        logger.error(f"Error processing question for file {filename}: {e}")
        flash('An error occurred while answering the question')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=8080)