from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Allow CORS for frontend domain
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Temporarily allow all origins

# Load API key securely
api_key = os.getenv("AI_SECRET")
if not api_key:
    raise ValueError("API key not found. Set the GOOGLE_GENAI_API_KEY environment variable.")

genai.configure(api_key=api_key)

BOT_NAME = "AI_BOT"

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Initialize the Generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def generate_response(user_message):
    try:
        combined_message = f"User: {user_message}\n{BOT_NAME}:"
        result = model.generate_content([combined_message])
        return result.text.strip() if hasattr(result, "text") else "No response from the model."
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route("/", methods=['GET'])
def home():
    return jsonify({"message": "Flask chatbot is running!"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try: 
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        bot_response = generate_response(user_message)

        response = jsonify({'response': bot_response})
        response.headers.add("Access-Control-Allow-Origin", "*")  # Allow all origins
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")

        return response, 200

    except Exception as e:
        return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500

# Handle CORS preflight requests
@app.route('/chat', methods=['OPTIONS'])
def chat_options():
    response = jsonify({'message': 'CORS preflight success'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response, 200

# Needed for Vercel
def handler(event, context):
    return app(event, context)
