from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from transformers import pipeline
import nltk
import torch
import sys
import os

# Download NLTK data
nltk.download('punkt')

# Add scraper.py path for import
sys.path.append('/content/drive/MyDrive/ai-fact-checker/backend')
try:
    from scraper import scrape_article
except ImportError:
    print("Error: scraper.py not found in /content/drive/MyDrive/ai-fact-checker/backend")
    sys.exit(1)

def setup_fact_checker():
    try:
        # Sample verified facts
        verified_facts = [
            "The moon landing occurred in 1969.",
            "COVID-19 vaccines are safe and effective, as per WHO.",
            "The earth is an oblate spheroid."
        ]
        
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Split facts into documents
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = text_splitter.create_documents(verified_facts)
        
        # Initialize Chroma DB
        os.makedirs("/content/drive/MyDrive/ai-fact-checker/chroma_db", exist_ok=True)
        db = Chroma.from_documents(documents, embeddings, persist_directory="/content/drive/MyDrive/ai-fact-checker/chroma_db")
        db.persist()
        
        return db, embeddings
    except Exception as e:
        print(f"Error setting up fact checker: {str(e)}")
        return None, None

def fact_check_article(text):
    try:
        if not text.strip():
            return [{"error": "No text provided for fact-checking"}]
        
        # Split text into sentences (claims)
        sentences = nltk.sent_tokenize(text)
        claims = sentences[:3]  # Limit to first 3 sentences for simplicity
        
        # Setup fact checker
        db, embeddings = setup_fact_checker()
        if db is None or embeddings is None:
            return [{"error": "Failed to initialize fact checker"}]
        
        # Initialize classifier
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        results = []
        for claim in claims:
            # Find similar facts
            claim_embedding = embeddings.embed_query(claim)
            similar_docs = db.similarity_search_by_vector(claim_embedding, k=1)
            if similar_docs:
                similar_fact = similar_docs[0].page_content
                # Classify claim against fact
                result = classifier(
                    claim,
                    candidate_labels=[f"True: {similar_fact}", f"False: contradicts {similar_fact}"],
                    hypothesis_template="This claim is {}."
                )
                fact_check = result["labels"][0]
                score = result["scores"][0]
                results.append({"claim": claim, "fact_check": f"{fact_check} (confidence: {score:.2f})"})
            else:
                results.append({"claim": claim, "fact_check": "No relevant fact found"})
        
        return results
    except Exception as e:
        return [{"error": f"Fact-checking error: {str(e)}"}]

if __name__ == "__main__":
    # Test with URL
    url = "https://www.bbc.com/news/articles/cm2erkr1n15o"
    article_data = scrape_article(url)
    if "error" not in article_data:
        text = article_data.get("text", "")
        results = fact_check_article(text)
        for result in results:
            print(f"Claim: {result.get('claim', '')}")
            print(f"Fact-Check: {result.get('fact_check', result.get('error', ''))}\n")
    else:
        print(f"Scraping error: {article_data['error']}")
