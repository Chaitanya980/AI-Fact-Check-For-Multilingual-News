import streamlit as st
import sys
import nltk

# Download NLTK data
nltk.download('punkt')

# Add backend path for imports
sys.path.append('/content/drive/MyDrive/ai-fact-checker/backend')
try:
    from scraper import scrape_article
    from translation import translate_text
    from fact_checker import fact_check_article
except ImportError as e:
    st.error(f"Import error: {str(e)}. Ensure backend files are in /content/drive/MyDrive/ai-fact-checker/backend")
    st.stop()

st.title("AI Fact Checker for Multilingual News")

# Input type selection
input_type = st.radio("Input Type", ["URL", "Text"])

# Input field
if input_type == "URL":
    user_input = st.text_input("Enter URL")
else:
    user_input = st.text_area("Enter Text")

# Translation direction
translation_direction = st.selectbox("Translation Direction", ["Spanish to English", "English to Spanish"])
source_lang = "es" if translation_direction == "Spanish to English" else "en"
target_lang = "en" if translation_direction == "Spanish to English" else "es"

# Process button
if st.button("Process"):
    if not user_input:
        st.error("Please provide a URL or text.")
    else:
        with st.spinner("Processing..."):
            # Translate input
            input_type_lower = "url" if input_type == "URL" else "text"
            translated_text = translate_text(user_input, input_type=input_type_lower, source_lang=source_lang, target_lang=target_lang)
            
            if translated_text.startswith("Scraping error") or translated_text.startswith("Translation error"):
                st.error(translated_text)
            else:
                st.subheader("Translated Text")
                st.write(translated_text)
                
                # Fact-check (in English)
                fact_check_input = translated_text if target_lang == "en" else user_input if input_type == "text" and source_lang == "en" else translate_text(user_input, input_type=input_type_lower, source_lang=source_lang, target_lang="en")
                fact_check_results = fact_check_article(fact_check_input)
                
                st.subheader("Fact-Check Results")
                for result in fact_check_results:
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.write(f"**Claim**: {result['claim']}")
                        st.write(f"**Fact-Check**: {result['fact_check']}")
                        st.markdown("---")
                    
                    # Translate results if target is Spanish
                    if target_lang == "es" and "claim" in result:
                        translated_claim = translate_text(result["claim"], input_type="text", source_lang="en", target_lang="es")
                        translated_fact_check = translate_text(result["fact_check"], input_type="text", source_lang="en", target_lang="es")
                        st.write(f"**Claim (Spanish)**: {translated_claim}")
                        st.write(f"**Fact-Check (Spanish)**: {translated_fact_check}")
                        st.markdown("---")
