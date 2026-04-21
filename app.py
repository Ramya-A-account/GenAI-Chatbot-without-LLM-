from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import json
import random
import requests

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Chatbot is running 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)












app = Flask(__name__)
CORS(app)

# Load ML
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Load intents
with open("intents.json") as f:
    intents = json.load(f)

# Context memory
last_events = []
last_tag = ""

# -------------------------
# Helper: Predict intent
# -------------------------
def predict(text):
    X = vectorizer.transform([text])
    return model.predict(X)[0]

# -------------------------
# Helper: Response
# -------------------------
def get_response(tag):
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return "Sorry, I didn't understand."

# -------------------------
# Helper: Location detect
# -------------------------
def extract_location(text):
    cities = ["chennai", "hyderabad", "bangalore", "mumbai", "delhi"]

    for city in cities:
        if city in text.lower():
            return city
    return "india"

# -------------------------
# 🔥 REAL EVENTS API
# -------------------------
def fetch_events(query):
    try:
        url = "https://serpapi.com/search.json"

        search_query = f"{query} events in Chennai India exhibition OR hackathon OR tech fest"

        params = {
            "engine": "google_events",
            "q": search_query,
            "hl": "en",
            "gl": "in",
            "api_key": "79dc0d4545bd49b011be5e6e0ccb7e81f87e497bebb33ca3e9b901c6892a7565"
        }

        res = requests.get(url, params=params)
        data = res.json()

        events = []

        for e in data.get("events_results", [])[:5]:
            title = e.get("title", "No title")
            date = e.get("date", {}).get("when", "No date")
            location = e.get("address", "No location")

            events.append(f"{title} | {date} | {location}")

        if not events:
            return [
                "Tech Expo – IIT Madras | Chennai",
                "Science Exhibition – Anna University | Chennai"
            ]

        return events

    except:
        return [
            "⚠️ API issue, showing sample events",
            "Tech Fest – IIT Madras"
        ]

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global last_events, last_tag

    user = request.json["message"].lower()

    # -------------------------
    # 🔥 FOLLOW-UP: LINKS
    # -------------------------
    if "link" in user or "apply" in user:

        if last_events and isinstance(last_events[0], dict):
            links = []
            for job in last_events:
                links.append(f"{job['title']} 👉 {job['link']}")

            return jsonify({
                "response": "Here are application links 👇",
                "events": links
            })

        return jsonify({
            "response": "No links available.",
            "events": []
        })

    # -------------------------
    # 🔥 FOLLOW-UP: DETAILS
    # -------------------------
    if "details" in user or "those" in user:

        if last_events:
            display = []

            for e in last_events:
                if isinstance(e, dict):
                    display.append(e["title"])
                else:
                    display.append(e)

            return jsonify({
                "response": "Here are the details again 👇",
                "events": display
            })

        return jsonify({
            "response": "No previous data available.",
            "events": []
        })

    # -------------------------
    # NORMAL FLOW
    # -------------------------
    tag = predict(user)
    response = get_response(tag)

    events = []

    if tag == "hackathon":
        events = fetch_events("hackathon")

    elif tag == "exhibition":
        events = fetch_events("college exhibition")

    elif tag == "conference":
        events = fetch_events("conference")

    elif tag == "sports":
        events = fetch_events("sports competition")

    elif tag == "jobs":
        location = extract_location(user)

        events = [
            {
                "title": f"Software Developer Jobs in {location.title()}",
                "link": f"https://www.linkedin.com/jobs/search/?keywords=software%20developer&location={location}"
            },
            {
                "title": f"Data Analyst Jobs in {location.title()}",
                "link": f"https://www.indeed.com/jobs?q=data+analyst&l={location}"
            },
            {
                "title": f"UI/UX Designer Jobs in {location.title()}",
                "link": f"https://www.naukri.com/ui-ux-designer-jobs-in-{location}"
            }
        ]

    # -------------------------
    # FORMAT OUTPUT
    # -------------------------
    display_events = []

    for e in events:
        if isinstance(e, dict):
            display_events.append(e["title"])
        else:
            display_events.append(e)

    # Save context
    last_events = events
    last_tag = tag

    return jsonify({
        "response": response,
        "events": display_events
    })

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)