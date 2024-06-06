# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for PyMuPDF

def pdf_to_documents(pdf_path):
    """
    Converts a PDF to a list of 'documents' which are chunks of a larger document that can be easily searched 
    and processed by the Cohere LLM. Each 'document' chunk is a dictionary with a 'title' and 'snippet' key
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries representing the documents. Each dictionary has a 'title' and 'snippet' key.
        Example return value: [{"title": "Page 1 Section 1", "snippet": "Text snippet..."}, ...]
    """

    doc = fitz.open(pdf_path)
    documents = []
    text = ""
    chunk_size = 1000
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        part_num = 1
        for i in range(0, len(text), chunk_size):
            documents.append({"title": f"Page {page_num + 1} Part {part_num}", "snippet": text[i:i + chunk_size]})
            part_num += 1
    return documents

# Add a sidebar to the Streamlit app
with st.sidebar:
    if hasattr(st, "secrets"):
        if "COHERE_API_KEY" in st.secrets.keys():
            cohere_api_key = st.secrets["COHERE_API_KEY"]
            # st.write("API key found.")
        else:
            cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
            st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    
    my_documents = []
    tone = []
    selected_tone = st.selectbox("Select your tone", ["Default", "Formal", "Semi-formal", "Casual"])
    if selected_tone == "Fomal":
        tone = "Formal"
    elif selected_tone == "Semiformal":    
        tone = "Semi-formal"
    elif selected_tone == "Casual":    
        tone = "Casual"
    else:
        tone = "Default"

    st.write(f"Selected tone: {selected_tone}")

    voice = []
    selected_voice = st.selectbox("Select your voice", ["Default", "Humorous", "Informative", "Authoritative", "Conversational", "Pleading"])
    if selected_voice == "Humorous":
        voice = "Humorous"
    elif selected_voice == "Informative":    
        voice = "Informative"
    elif selected_voice == "Authoritative":    
        voice = "Authoritative"
    elif selected_voice == "Conversational":    
        voice = "Conversational"
    elif selected_voice == "Pleading":    
        voice = "Pleading"
    else:
        tone = "Default"

    st.write(f"Selected voice: {selected_voice}")
    

# Set the title of the Streamlit app
st.title("💬 Email Drafter")

# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "text": "Hi! I am a email drafter bot that can help you write any kind of email you want given a description of the prompt."}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Get user input
if prompt := st.chat_input():
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("user").write(prompt)

    preamble = """You are an Email Drafting Assistant, designed to help users compose effective and professional emails.
     Your goal is to generate email drafts that align with the specified tone while following a structured format.
     Please adhere to the following guidelines: Email Title: Begin the email draft by including a clear and concise title or subject line that accurately reflects the purpose of the email.
      If no specific title is provided in the prompt, generate a suitable title based on the context. 
      Greetings: Determine the appropriate greeting based on the specified tone. If a formal tone is required, use formal greetings such as "Dear Mr./Ms. [Last Name]."
      For a semi-formal tone, opt for greetings like "Hello [First Name]." In the case of an casual tone, consider using greetings like "Hi [First Name]." 
      By default, if selected_tone = default, formulate a respectful email. Formulate the tone based on the recipient. For example, is the recipient is a teacher, use a formal tone; if recipient is a friend, use semi-formal or informal tone.
      Actual Message: Generate the main body of the email, taking into account the specified tone. 
      Use language and phrasing that align with the desired tone, whether it's formal, friendly, persuasive, or informative. Ensure the content is clear, concise, and relevant to the purpose of the email. 
      Incorporate any specific details or requests provided in the prompt. 
      Closing: Select an appropriate closing based on the specified tone. For formal emails, use closings like "Sincerely," "Best regards," or "Yours faithfully." 
      If the tone is semi-formal or casual, consider closings such as "Kind regards," "Thank you," or "Take care." If no specific tone is indicated, default to a formal closing. 
      Sender's Name: Sign off the email with the sender's name in a manner that matches the specified tone. If a formal tone is required, use the full name or a professional title. 
      For a semi-formal or casual tone, the first name or a less formal signature may be appropriate.
      For casual tone, the email should usually be more straightforward and shorter.

      Voice is the style of writing that expresses the tone.
    Conversational: A conversational email voice is like having a conversation with someone. Use simple, clear language and avoid overly technical words or jargon. The goal is to make the email feel more like a chat than a formal email. Some examples could be using personal stories, using contractions, and including questions.
    Authoritative: An authoritative email voice is professional and confident. Your email should be clear and concise, but still, have a sense of authority behind it. Avoid slang or overly conversational language – stick to facts and figures that support your message.
    Informative: An informative email voice is similar to an authoritative email voice, but with a focus on providing information. Your email should be clear and easy to understand, with plenty of facts and figures to back up your message.
    Pleading: Showing in an emotional way that you want something urgently.
    Humorous: Consider adding a P.S. at the end of the email, and incorporating callbacks. Maybe make some jokes but keep the jokes lighthearted and respectful.

    By default, do not add a P.S. at the end of the email unless specified.
    """

    prompt = prompt + f"               ;Respond in the following tone: {selected_tone}, voice: {selected_voice}"

    # Send the user message and pdf text to the model and capture the response
    response = client.chat(chat_history=st.session_state.messages,
                           message=prompt,
                           # documents=my_documents,
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    # Add the response to the chat history
    msg = response.text
    st.session_state.messages.append({"role": "assistant", "text": msg})

    # Write the response to the chat window
    st.chat_message("assistant").write(msg)