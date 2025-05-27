from newspaper import Article
import json
import os

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        data = {
            "title": article.title,
            "text": article.text,
            "source": article.source_url,
            "publish_date": str(article.publish_date)
        }
        # Save to Google Drive in Colab
        os.makedirs("/content/drive/MyDrive/ai-fact-checker/data", exist_ok=True)
        with open("/content/drive/MyDrive/ai-fact-checker/data/articles.json", "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example URL for testing
    url = "https://www.bbc.com/news/articles/cm2erkr1n15o"
    article_data = scrape_article(url)
    print(json.dumps(article_data, indent=4))
