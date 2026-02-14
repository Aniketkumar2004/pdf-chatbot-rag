import streamlit as st
import requests
import io

API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="PDF Chatbot", page_icon="📚", layout="wide")

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_pdf(file):
    try:
        file_bytes = file.read()
        file.seek(0)
        files = {"file": (file.name, io.BytesIO(file_bytes), "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.json().get('detail', 'Upload failed')}"
    except Exception as e:
        return None, str(e)

def query_documents(question, top_k=5):
    payload = {"question": question, "top_k": top_k}
    try:
        response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=60)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.json().get('detail', 'Query failed')}"
    except Exception as e:
        return None, str(e)

def list_documents():
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, "Failed"
    except Exception as e:
        return None, str(e)

def delete_document(doc_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{doc_id}", timeout=30)
        return response.status_code == 200, None
    except Exception as e:
        return False, str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("PDF Chatbot with RAG")
    
    if not check_api_health():
        st.error("Backend API is not running!")
        st.stop()
    
    with st.sidebar:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Choose PDF", type=["pdf"])
        
        if uploaded_file and st.button("Upload"):
            with st.spinner("Processing..."):
                result, error = upload_pdf(uploaded_file)
                if result:
                    st.success(f"Uploaded: {result['filename']}")
                    st.info(f"Pages: {result['num_pages']} | Chunks: {result['num_chunks']}")
                else:
                    st.error(error)
        
        st.divider()
        st.subheader("Documents")
        docs_data, _ = list_documents()
        if docs_data and docs_data['total_count'] > 0:
            st.metric("Total", docs_data['total_count'])
        else:
            st.info("No documents")
        
        top_k = st.slider("Sources", 1, 10, 5)
    
    st.header("Chat")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result, error = query_documents(prompt, top_k)
                if result:
                    st.markdown(result["answer"])
                    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
                else:
                    st.error(error)

if __name__ == "__main__":
    main()