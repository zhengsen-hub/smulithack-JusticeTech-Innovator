from util import *
from streamlit_option_menu import option_menu
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Legal Support Chat", page_icon=":judge:", layout="centered")

# --- SETUP SESSION STATE VARIABLES ---
if "vector_store" not in st.session_state:
    st.session_state.vector_store = False
if "response" not in st.session_state:
    st.session_state.response = None
if "prompt_activation" not in st.session_state:
    st.session_state.prompt_activation = False
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = None
if "prompt" not in st.session_state:
    st.session_state.prompt = False

load_dotenv()

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header('Configuration')
groq_api_key = sidebar_api_key_configuration()
model = sidebar_groq_model_selection()

# --- MAIN PAGE CONFIGURATION ---
st.title("Legal Chat :closed_book:")
st.write("*Think of this chatbot as a helpful guide, not a lawyer. It can point you in the right direction, but for legal matters, it's best to consult with a professional*")
st.write(":red[***Disclaimer: While we strive to provide helpful information, the chatbot's responses are not guaranteed to be correct or complete. It is essential to verify any information obtained from the chatbot with reliable sources.***]")
st.write(':blue[***Powered by Groq AI Inference Technology***]')

# ---- NAVIGATION MENU -----
selected = option_menu(
    menu_title=None,
    options=["Legal Chat", "Reference", "Contact Legal Support", "About"],
    icons=["robot", "bi-file-text-fill", "question-circle-fill", "app"],  # https://icons.getbootstrap.com
    orientation="horizontal",
)

llm = ChatGroq(groq_api_key=groq_api_key, model_name=model)

prompt = ChatPromptTemplate.from_template(
    """
    Answer the question based on the provided context only. If question is not within the context, do not try to answer
    and respond that the asked question is out of context or something similar.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    Questions: {input}
    """
)
# ----- SETUP Doc Chat MENU ------
if selected == "Legal Chat":
    st.subheader("Upload PDF(s)")
    pdf_docs = st.file_uploader("Upload your PDFs", type=['pdf'], accept_multiple_files=True,
                                disabled=not st.session_state.prompt_activation, label_visibility='collapsed')
    process = st.button("Process", type="primary", key="process", disabled=not pdf_docs)

    if process:
        with st.spinner("Processing ..."):
            st.session_state.vector_store = create_vectorstore(pdf_docs)
            st.session_state.prompt = True
            st.success('Database is ready')

    st.divider()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": """Hi, I am here to help provide general information on your legal query. 
                                         \n Please take note that this is only intended as a preliminary information tool only and should not be considered legal advice. \n
                                         \n The information will come from relevant statutory laws & provisions, case laws and previous cases.
                                         \n *Example: Can an organisation collect, use or disclose publicly available personal data for any purposes?*
                                         """}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    container = st.container(border=True)
    if question := st.chat_input(placeholder='Enter your question related to uploaded document',
                                 disabled=not st.session_state.prompt):
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        with st.spinner('Processing...'):
            st.session_state.response = get_llm_response(llm, prompt, question)
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.response['answer']})
            st.chat_message("assistant").write(st.session_state.response['answer'] + "\n\n" +":red[***Disclaimer: While we strive to provide helpful information, the chatbot's responses are not guaranteed to be correct or complete. It is essential to verify any information obtained from the chatbot with reliable sources.***]")

# ----- SETUP REFERENCE MENU ------
if selected == "Reference":
    st.title("Reference & Context")
    if st.session_state.response is not None:
        for i, doc in enumerate(st.session_state.response["context"]):
            with st.expander(f'Reference # {i + 1}'):
                st.write(doc.page_content)

# ----- SETUP ASKFORHELP MENU ------
if selected == "Contact Legal Support":
    st.title("Contact Legal Support")
    st.write(""":red[**Disclaimer: Deemed Consent**]
                \n By using this feature, you are providing your 'deemed consent' to the collection, use, and disclosure of your personal data by us for the purposes outlined in our Privacy Policy. 

                \n 'Deemed consent' means that if you voluntarily provide your personal data to us, it is assumed that you consent to the collection, use, and disclosure of your personal data for the purposes that would be considered obvious to a reasonable person in the circumstances and for which you have provided the personal data.

                \n If you do not agree with these terms, please refrain from using this feature. We reserve the right to change our policy at any time, and we will post those changes on this page. Please check back periodically to ensure you are aware of any changes.
             """)

    if st.session_state.response is not None:
        with st.expander("Draft Email for Legal Advice"):
            # Combining the user’s question, chatbot’s response, and the references into an email draft
            email_body = f"""
            Dear Legal Team,

            I hope this message finds you well.

            I have a legal question and would greatly appreciate your assistance.

            **Question:**
            {st.session_state.messages[-2]['content']}

            **Chatbot's Response:**
            {st.session_state.response['answer']}

            **References:**
            """
            for i, doc in enumerate(st.session_state.response["context"]):
                email_body += f"Reference {i + 1}: {doc.page_content}\n"

            st.session_state.email_draft = email_body
            st.markdown(email_body)

        additional_input = st.chat_input(
            placeholder="Add any additional information or clarification for the legal team before sending",
            key="additional_input"
        )

        if additional_input:
            st.session_state.email_draft += f"\n\n**Additional Information:**\n{additional_input}\n"
            st.session_state.email_draft += """\n Thank you.
            \n Yours Sincerely,
            \n ```name of user```
            """
            st.markdown(st.session_state.email_draft)
        else:
            st.session_state.email_draft += """\n Thank you.
            \n Yours Sincerely,
            \n ```name of user```
            """
            st.markdown(st.session_state.email_draft)

        if st.button("Send Email", type="primary", key="send_email"):
            send_email_to_legal_team(st.session_state.email_draft)  # You need to define this function
            st.success("Email sent successfully!")

# ----- SETUP ABOUT MENU ------
if selected == "About":
    with st.expander("About this App"):
        st.markdown(''' This chatbot offers basic information and potential resources related to your query. However, it cannot provide specific legal advice or create an attorney-client relationship. For accurate and tailored legal guidance, please consult with an attorney. It has following functionality:

    - Provide information from relevant statutory laws & provisions, case laws and previous cases
    - Support of Groq AI inference technology (Only available in development phase)
    - Display the response context and document reference
    - Draft email to enable extension of support to those in legal practice. 

        ''')
    with st.expander("Which Large Language models are supported by this App?"):
        st.markdown(''' This app supports the following LLMs as supported by Groq:

    - Chat Models -- Groq
        - Llama3-8b-8192 
        - Llama3-70b-8192 
        - Mixtral-8x7b-32768
        - Gemma-7b-it
        ''')

    with st.expander("Which library is used for vectorstore?"):
        st.markdown(''' This app supports the FAISS for AI similarity search and vectorstore:
        ''')

    with st.expander("Whom to contact regarding this app?"):
        st.markdown(''' Contact [MinLaw](xxx@gmail.com)
        ''')
