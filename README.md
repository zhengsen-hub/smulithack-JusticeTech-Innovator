# JusticeTech-Innovator Chat
RAG based generative AI application to demo chatbot using PDF documents as knowledge base.
Developed using Streamlit and Groq AI Inference technology.

## Key Features
- **1. PDF Upload and Processing:** Multiple PDF uploads for AI chatbot.
- **2. Reference and Context Display:** Shows context and document references used by the AI (transparency of how AI chatbot formulate responses).
- **3. Contact Legal Support:** Prepare a draft email containing the following: 
    - user's question
    - chatbot's formulated responses and references used
    - additional user inputs
    - Send Email button
- **4. Model Selection:** Offers various Groq AI models for optimal performance.
- **5. Powered by FAISS:** Utilizes FAISS for efficient similarity search and vector storage.

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Groq AI, FAISS (Vector Store)

# Installation
1. Clone this repository
2. Create and activate virtual environment
    
    `Set-ExecutionPolicy -Scope Process Unrestricted`
    
    `.\venv\Scripts\activate.ps1`
3. Install the necessary python packages:

   `pip install -r requirements.txt`
5. Run the application with following command from terminal:

   `streamlit run main.py`