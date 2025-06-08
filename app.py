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
def google_search(query, api_key, cse_id, num_results=3):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&num={num_results}"
    response = requests.get(url)
    data = response.json()
    snippets = []
    if "items" in data:
        for item in data["items"]:
            snippets.append(f"{item['title']}: {item['snippet']}")
    return "\n".join(snippets)

# --- Answer Generator ---
def get_answer(user_question):
    search_prompt = f"Generate a web search query to answer: {user_question}"
    search_query = model.generate_content(search_prompt).text.strip()
    search_results = google_search(search_query, GOOGLE_API_KEY, CSE_ID)

    synthesis_prompt = f"""
    You are an assistant helping users understand Indian government schemes.

    Use the search results below to answer the question:
    Search Results:
    {search_results}

    Question:
    {user_question}
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
