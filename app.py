# OpenGovAI: An AI Agent for Citizen Queries on Government Schemes

import streamlit as st
import google.generativeai as genai
import requests
import os

# Setup keys from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-001")

# Google Search Helper
def google_search(query, api_key, cse_id, num_results=10):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&num={num_results}"
    response = requests.get(url)
    data = response.json()
    snippets = []
    if "items" in data:
        for item in data["items"]:
            snippet = item['snippet'] if 'snippet' in item else ''
            link = item['link'] if 'link' in item else ''
            title = item['title'] if 'title' in item else ''
            # Format result as hyperlink that opens in new tab
            snippets.append(f"<a href='{link}' target='_blank'>{title}</a>: {snippet}")
    return "<br><br>".join(snippets)

# Answer Generator
def get_answer(user_question):
    # Smart query generation
    search_prompt = f"""
    You are helping users find government scheme details like eligibility, launch year, and benefits.

    Convert the question into a highly effective Google search query that will retrieve the most relevant results.

    User Question: {user_question}
    Search Query:
    """
    search_query = model.generate_content(search_prompt).text.strip()

    # Perform web search
    search_results = google_search(search_query, GOOGLE_API_KEY, CSE_ID)

    # Focused answer synthesis with request for elaboration
    synthesis_prompt = f"""
    You are a highly knowledgeable government policy assistant. Based ONLY on the search results provided below, answer the user's question in a detailed, well-structured, and informative manner. Ensure the following:

    - Provide scheme introduction year if available
    - Mention relevant departments, ministries, or officials
    - Clearly list benefits, eligibility criteria, and procedures
    - Include contextual details and real-world examples if available
    - Where useful, link to source material using HTML anchor tags with target='_blank'

    If the specific answer cannot be found, politely say: "Sorry, I couldn’t find the specific information in the search results."

    Search Results:
    {search_results}

    User Question:
    {user_question}

    Detailed Answer:
    """
    response = model.generate_content(synthesis_prompt)
    return response.text.strip()

# Streamlit Chatbot-style UI
st.set_page_config(page_title="OpenGovAI", layout="centered")
st.title("OpenGovAI 🇮🇳")
st.subheader("Ask anything about Government Schemes")

# Chat history management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User query input
user_input = st.chat_input("Ask about a scheme, its benefits, or launch year...")
if user_input:
    with st.spinner("Analyzing your query..."):
        answer = get_answer(user_input)
        st.session_state.chat_history.append((user_input, answer))

# Display chat history
for q, a in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        st.markdown(a, unsafe_allow_html=True)
