import json
import pickle
import random
import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

# Load model
model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

# Load intents
with open('intents.json') as file:
    data = json.load(file)

# 🔥 EVENT DATASET
events = [
    {"type": "hackathon", "domain": "UI/UX", "mode": "online", "location": "chennai", "name": "Design Hack 2026"},
    {"type": "hackathon", "domain": "AI", "mode": "offline", "location": "chennai", "name": "AI Challenge Chennai"},
    {"type": "job", "domain": "software", "mode": "online", "location": "india", "name": "Junior Developer Role"},
    {"type": "sports", "domain": "cricket", "mode": "offline", "location": "chennai", "name": "Chennai Cricket League"},
    {"type": "exhibition", "domain": "science", "mode": "offline", "location": "school", "name": "Science Expo 2026"}
]

# 🧠 Preprocess
def preprocess(text):
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens if w.isalnum()]
    return " ".join(tokens)

# 🔍 Extract user details
def extract_details(text):
    text = text.lower()

    details = {
        "type": None,
        "domain": None,
        "mode": None,
        "location": None
    }

    # Type
    if "hackathon" in text or "competition" in text:
        details["type"] = "hackathon"
    elif "job" in text or "internship" in text:
        details["type"] = "job"
    elif "sports" in text or "cricket" in text:
        details["type"] = "sports"
    elif "exhibition" in text or "expo" in text:
        details["type"] = "exhibition"

    # Domain
    if "ui" in text or "ux" in text:
        details["domain"] = "UI/UX"
    elif "ai" in text:
        details["domain"] = "AI"
    elif "cricket" in text:
        details["domain"] = "cricket"

    # Mode
    if "online" in text:
        details["mode"] = "online"
    elif "offline" in text:
        details["mode"] = "offline"

    # Location
    if "chennai" in text:
        details["location"] = "chennai"

    return details

# 🔍 Filter events
def filter_events(details):
    results = []

    for event in events:
        match = True
        for key in details:
            if details[key] and event[key] != details[key]:
                match = False
                break
        if match:
            results.append(event)

    return results

# 💬 Get response
def get_response(tag):
    for intent in data['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return "Sorry, I didn't understand."

# 🚀 Chat loop
print("Chatbot ready! Type 'quit' to exit.")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Bot: Goodbye!")
        break

    # Step 1: Try filtering
    details = extract_details(user_input)
    results = filter_events(details)

    if results:
        print("Bot: Here are matching opportunities:")
        for r in results:
            print(f"- {r['name']} ({r['type']}, {r['mode']}, {r['location']})")
    else:
        # Step 2: ML fallback
        processed = preprocess(user_input)
        X = vectorizer.transform([processed])
        tag = model.predict(X)[0]

        response = get_response(tag)
        print("Bot:", response)