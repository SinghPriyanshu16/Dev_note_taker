import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure the API key if available
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def process_text_with_ai(text_content):
    """
    Calls the AI model to generate documentation, action items, and tech debt.
    """
    if not api_key:
        return {
            "error": "API key not configured. Please set GEMINI_API_KEY in your .env file."
        }
        
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        You are a senior developer assistant. I will provide you with a pull request description or a meeting transcript snippet.
        
        Please analyze it and provide the output in the following format:
        
        ### 📝 Documentation
        [Create a brief markdown documentation summarizing the context and changes]
        
        ### ✅ Action Items
        [List key action items as checkboxes]
        
        ### ⚠️ Technical Debt & Flags
        [Highlight any potential technical debt, code smells, or areas needing follow-up]
        
        Here is the input text:
        {text_content}
        """
        
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        print(f"Error calling AI: {e}")
        return {"error": "Failed to generate summary. See server logs for details."}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
        
    snippet = data.get('text', '').strip()
    if not snippet:
        return jsonify({'error': 'Text is empty'}), 400
        
    # Process the text
    result = process_text_with_ai(snippet)
    
    if "error" in result:
        return jsonify({'error': result["error"]}), 500
        
    return jsonify({'summary': result["result"]})

if __name__ == '__main__':
    # Run in debug mode for development
    app.run(debug=True, port=5000)
