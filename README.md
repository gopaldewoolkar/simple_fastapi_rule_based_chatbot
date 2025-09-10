# 🍽️ Simple FastAPI Rule Based Chatbot

A simple **FastAPI-based chatbot** that asks users a series of food preference questions, stores their responses, and provides a summary at the end.  
The chatbot uses a **decision tree approach** with predefined questions, options, and branching logic.

---

## 🚀 Features
- Interactive Q&A chatbot
- Predefined branching logic based on user choices
- Conversation history tracking
- Final summary of user preferences
- Built-in API documentation via Swagger UI

---

## 🛠️ Tech Stack
- **Python 3.8+**
- **FastAPI** (for API endpoints)
- **Pydantic** (for request/response validation)
- **Uvicorn** (for running the app)

---

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/reponame.git
   cd reponame
   ```

2. Create and Activate the virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

4. Running the Application
   ```bash
   uvicorn main:app --reload
   ```

## The API will be available at:
`Swagger Docs: http://127.0.0.1:8000/docs`
`Redoc Docs: http://127.0.0.1:8000/redoc`

## 📖 API Usage
Endpoint
`POST /chat`

### Request Body
```JSON
{
  "user_input": "Italian",
  "conversation_history": [
    {
      "question_id": "q1_food_type",
      "answer": "Italian"
    }
  ]
}
```

### Response
```JSON
{
  "message": "Do you prefer pasta or pizza?",
  "question_id": "q2_italian_preference",
  "options": ["Pasta", "Pizza"],
  "conversation_history": [
    {
      "question_id": "q1_food_type",
      "answer": "Italian"
    }
  ],
  "is_conversation_complete": false,
  "final_summary": null
}
```


## 🧩 Project Structure
```bash
.
├── main.py        # FastAPI application
├── README.md      # Documentation
```

## 📝 Notes

Modify the QUESTIONS dictionary in `main.py` to change the flow or add more questions.

Ensure that the `next_question_map` values are consistent to avoid invalid states.
