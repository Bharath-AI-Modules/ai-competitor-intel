import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Competitor Intel Scraper", page_icon="📊", layout="wide")

# Header & Branding
st.title("📊 AI Competitor Intelligence Scraper")
st.caption("Powered by **Bharath-AI-Modules** — Lightweight, modular intelligence tools.")

# Sidebar for API Configuration & Inbound Funnel
with st.sidebar:
    st.header("🔑 Authentication")
    user_api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("Don't have a key? Get one for free via Google AI Studio.")
    
    st.write("---")
    st.header("💼 Enterprise Integrations")
    st.markdown("""
    Need this automation scaled up? We specialize in:
    * 🏢 **Bulk Scraping:** Tracking 100+ sites simultaneously.
    * 📈 **CRM Syncing:** Piping insights to Google Sheets/Notion.
    * 📧 **Daily Email Alerts:** Tracking competitor modifications.
    """)
    st.markdown("[📩 **Hire Bharath-AI-Modules**](https://www.linkedin.com)")

# Main Interface Workspace
target_url = st.text_input("Enter the competitor landing page URL (e.g., https://example.com):")

if st.button("Generate Intelligence Report", type="primary"):
    if not user_api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed.")
    elif not target_url:
        st.warning("Please enter a target URL to analyze.")
    else:
        with st.spinner("Step 1/2: Extracting web data from landing page..."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(target_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                web_text = " ".join([p.get_text() for p in paragraphs])[:4000]
                
            except Exception as e:
                st.error(f"Failed to scrape the website: {e}")
                web_text = None

        if web_text and len(web_text) > 100:
            with st.spinner("Step 2/2: Processing tactical analysis with LLM..."):
                try:
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    prompt = f"""
                    You are a premium business intelligence analyst. Analyze the following raw text scraped from a business competitor's website. Provide a professional, structured markdown summary highlighting:
                    1. Core Value Proposition (What do they sell/solve?)
                    2. Key Target Audience
                    3. Identified Strengths & Weaknesses based on copy
                    4. Marketing or Messaging Angles used

                    Raw Web Content:
                    \"\"\"{web_text}\"\"\"
                    """
                    
                    ai_response = model.generate_content(prompt)
                    
                    st.success("Analysis Complete!")
                    st.subheader("📊 Tactical Competitor Intelligence Report")
                    st.markdown(ai_response.text)
                    
                except Exception as e:
                    st.error(f"AI Generation Error: {e}")
        else:
            if web_text:
                st.error("Could not extract sufficient text content from this page layout.")
