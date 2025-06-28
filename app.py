# app.py

import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load Environment Variables ---
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# --- Configure API Clients ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found. Agent will not work.")


# --- Agent Tool Functions ---

def parse_ai_summary_to_json(summary_text: str):
    """
    Parses the plain text summary from the AI into a structured JSON object.
    This version is more robust and can handle multi-line values.
    """
    summary_data = {}
    current_key = None
    current_value = ""

    # A mapping of the keys we are looking for
    key_map = {
        "revenue_summary": "revenue_summary",
        "net_income_summary": "net_income_summary",
        "ceo_quote": "ceo_quote",
        "strategic_focus": "strategic_focus",
        "source_url": "source_url"
    }

    lines = summary_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line starts with one of our known keys
        found_key = None
        for key, field_name in key_map.items():
            if line.lower().startswith(f"- {key}:") or line.lower().startswith(f"{key}:"):
                found_key = field_name
                break

        if found_key:
            # If we found a new key, save the previous key-value pair
            if current_key and current_value:
                summary_data[current_key] = current_value.strip()
            
            # Start tracking the new key
            current_key = found_key
            # Get the initial value on the same line
            current_value = line.split(":", 1)[1].strip()
        elif current_key:
            # If it's not a new key, append the line to the current value
            current_value += " " + line

    # Save the last key-value pair after the loop finishes
    if current_key and current_value:
        summary_data[current_key] = current_value.strip()
        
    # Specifically parse the strategic focus into a list
    if 'strategic_focus' in summary_data and isinstance(summary_data['strategic_focus'], str):
        summary_data['strategic_focus'] = [item.strip() for item in summary_data['strategic_focus'].split(',')]

    # Final check for an error message in the raw text
    if "could not find" in summary_text.lower() or "unable to" in summary_text.lower():
        summary_data["error"] = summary_text
        
    return summary_data


def get_financial_summary_with_search(company: str, quarter: str):
    """
    This function uses Gemini with its integrated Google Search tool
    and then parses the text response into a JSON object.
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API Key not configured."}

    print(f"--- Agent Step: Starting search & summary for {company} {quarter} ---")
    
    prompt = f"""
    You are a financial analyst. Find the most recent official earnings report or press release for {company}'s {quarter}. 
    Based *only* on the information you find, provide a concise summary.
    
    Structure your response using the following headings on separate lines, followed by the data:
    - revenue_summary:
    - net_income_summary:
    - ceo_quote:
    - strategic_focus: (as a comma-separated list)
    - source_url:

    If you cannot find a relevant document, respond with only one line: "Error: Could not find a relevant financial document."
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', tools=['google_search_retrieval'])
        response = model.generate_content(prompt)
        
        print(f"--- Raw AI Response ---\n{response.text}\n--------------------")
        
        parsed_summary = parse_ai_summary_to_json(response.text)
        return parsed_summary

    except Exception as e:
        print(f"An error occurred during AI processing: {e}")
        return {"error": f"Failed to generate summary: {str(e)}"}


# --- API Endpoints ---
@app.route("/")
def home():
    return render_template('index.html')

@app.route('/analyze')
def analyze_endpoint():
    company = request.args.get('company')
    quarter = request.args.get('quarter')

    if not company or not quarter:
        return jsonify({"error": "Please provide both 'company' and 'quarter' parameters."}), 400
    
    final_summary = get_financial_summary_with_search(company, quarter)
    
    if final_summary.get("error") and final_summary.get("error"):
         return jsonify({"error": final_summary["error"]}), 500
         
    return jsonify(final_summary)


@app.route("/ping", methods=["GET"])
def ping():
    return {"ok": True}, 200

# --- Run the Server ---
if __name__ == '__main__':
    app.run(debug=True, port=8080)
