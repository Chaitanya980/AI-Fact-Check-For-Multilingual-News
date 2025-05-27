from transformers import MarianMTModel, MarianTokenizer
import os
import sys

# Add scraper.py path for import
sys.path.append('/content/drive/MyDrive/ai-fact-checker/backend')
from scraper import scrape_article

def translate_text(input_data, input_type="text", source_lang="es", target_lang="en"):
    try:
        # Handle URL input
        if input_type == "url":
            article_data = scrape_article(input_data)
            if "error" in article_data:
                return f"Scraping error: {article_data['error']}"
            text = article_data.get("text", "")
            if not text:
                return "No text extracted from the URL. Check the URL or scraped content."
        else:
            text = input_data
            if not text.strip():
                return "No text provided."
        
        # Perform translation
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        
        # Split text into chunks to handle long inputs
        max_length = 512
        sentences = text.split(". ")
        translated_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=max_length)
                translated = model.generate(**inputs)
                translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
                translated_sentences.append(translated_text)
        
        return ". ".join(translated_sentences)
    except Exception as e:
        return f"Translation error: {str(e)}"

if __name__ == "__main__":
    # Test URL input, English to Spanish
    url = "https://www.bbc.com/news/articles/cm2erkr1n15o"
    translated_es = translate_text(url, input_type="url", source_lang="en", target_lang="es")
    print(f"URL (English to Spanish):\n{translated_es}\n")
    
    # Test text input, Spanish to English
    sample_text_es = "Este es un artículo de noticias en español."
    translated_en = translate_text(sample_text_es, input_type="text", source_lang="es", target_lang="en")
    print(f"Text (Spanish to English):\n{translated_en}\n")
    
    # Test text input, English to Spanish
    sample_text_en = "This is a news article in English."
    translated_es = translate_text(sample_text_en, input_type="text", source_lang="en", target_lang="es")
    print(f"Text (English to Spanish):\n{translated_es}")
