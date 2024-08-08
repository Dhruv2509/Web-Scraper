from flask import Flask, request, jsonify
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)

# Hardcoded OpenAI API key
api_key = 'sk-9-5QGSayZkD8T-1AQae5V0IgLx4HeA9-ks8Pofoo4ET3BlbkFJSL_msr9a-envL5Su0chjgjwjsXx6hqkgXQyX5iioAA'

def get_articles(query):
    articles = []
    search_results = search(query, num_results=10)  # Adjust the number of results as needed

    for url in search_results:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Simplistic approach; you'll need to adjust the selector based on the site
            paragraphs = soup.find_all('p')
            full_text = ' '.join([para.get_text() for para in paragraphs])
            articles.append({'url': url, 'text': full_text})
        except Exception as e:
            print(f"Failed to retrieve {url}: {e}")
    
    return articles

def analyze_text_with_openai(text):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"Can you share symptoms based on this text: {text}. Only diseases and symptoms in 20 words."
            }
        ],
        "temperature": 0.4,
        "max_tokens": 200
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

@app.route('/search', methods=['GET'])
def search_articles():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Get articles
    articles = get_articles(query)
    
    # Combine all article texts into a single field
    combined_text = ' '.join([article['text'] for article in articles])
    
    # Analyze text with OpenAI
    analysis_result = analyze_text_with_openai(combined_text)
    
    return jsonify({'analysis': analysis_result})

if __name__ == '__main__':
    app.run(debug=True)
