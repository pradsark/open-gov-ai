# OpenGovAI: An AI Agent for Citizen Queries on Government Schemes
# Streamlit App Version with Fixes

import streamlit as st
import google.generativeai as genai
import requests
import os

# --- Setup keys from Streamlit secrets ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]

# --- Configure Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-001")

# --- Google Search Helper ---
def google_search(query, api_key, cse_id, num_results=7):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&num={num_results}"
    response = requests.get(url)
    data = response.json()
    snippets = []
    if "items" in data:
        for item in data["items"]:
            snippets.append(f"{item['title']}: {item['snippet']} (Source: {item['link']})")
    return "\n".join(snippets)

# --- Answer Generator ---
def get_answer(user_question):
    # Smarter query generation
    search_prompt = f"""
    You are helping users find government scheme details like eligibility, launch year, and benefits.

    Convert the question into a highly effective Google search query that will retrieve the most relevant results.

    User Question: {user_question}
    Search Query:
    """
    search_query = model.generate_content(search_prompt).text.strip()

    # Perform web search
    search_results = google_search(search_query, GOOGLE_API_KEY, CSE_ID)

    # Focused answer synthesis
    synthesis_prompt = f"""
    You are a government policy assistant. Based ONLY on the search results provided below, answer the user's question with:

    - Specific dates (like scheme introduction year)
    - Names of ministries or departments
    - Benefits, eligibility, and timelines
    - If not found, respond: \"Sorry, I couldn’t find the specific information in the search results.\"

    Search Results:
    {search_results}

    User Question:
    {user_question}

    Answer:
    """
    response = model.generate_content(synthesis_prompt)
    return response.text.strip()

# --- Streamlit UI ---
st.set_page_config(page_title="OpenGovAI", layout="centered")
st.title("OpenGovAI 🇮🇳")
st.subheader("All about Government Schemes")

question = st.text_input(" Enter your question")
if st.button("Get Answer") and question:
    with st.spinner("Analyzing your query..."):
        answer = get_answer(question)
        st.markdown("### Results")
        st.markdown(answer)
