from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# Initialize FastAPI app
app = FastAPI(
    title="Simple Chatbot API",
    description="A chatbot that asks questions with options and stores responses.",
    version="1.0.0"
)

# --- Pydantic Models for Request and Response ---

class ConversationEntry(BaseModel):
    """Represents a single question-answer pair in the conversation history."""
    question_id: str = Field(..., description="The ID of the question asked.")
    answer: str = Field(..., description="The user's selected answer for the question.")

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    user_input: Optional[str] = Field(
        None,
        description="The user's answer to the current question. Leave empty for the first question."
    )
    conversation_history: List[ConversationEntry] = Field(
        [],
        description="A list of previous question-answer pairs. Send this back with each request."
    )

class ChatResponse(BaseModel):
    """Response body from the chat endpoint."""
    message: str = Field(..., description="The chatbot's message or question.")
    question_id: Optional[str] = Field(
        None,
        description="The ID of the current question being asked (if any)."
    )
    options: Optional[List[str]] = Field(
        None,
        description="List of available options for the current question."
    )
    conversation_history: List[ConversationEntry] = Field(
        ...,
        description="The complete conversation history, including the latest interaction."
    )
    is_conversation_complete: bool = Field(
        False,
        description="True if the conversation has reached its end."
    )
    final_summary: Optional[Dict[str, str]] = Field(
        None,
        description="A summary of the conversation if it's complete."
    )

# --- Chatbot Questions Configuration ---

# Define the questions, their options, and the logic for the next question.
# 'next_question_map' determines the next question based on the user's answer.
# 'end' signifies the end of a conversation branch.
QUESTIONS: Dict[str, Dict[str, Any]] = {
    "q1_food_type": {
        "question": "What kind of food are you in the mood for?",
        "options": ["Italian", "Mexican", "Indian"],
        "next_question_map": {
            "Italian": "q2_italian_preference",
            "Mexican": "q2_mexican_spice",
            "Indian": "q2_indian_dish"
        }
    },
    "q2_italian_preference": {
        "question": "Do you prefer pasta or pizza?",
        "options": ["Pasta", "Pizza"],
        "next_question_map": {
            "Pasta": "q3_pasta_sauce",
            "Pizza": "q3_pizza_toppings"
        }
    },
    "q2_mexican_spice": {
        "question": "Do you like your Mexican food spicy or mild?",
        "options": ["Spicy", "Mild"],
        "next_question_map": {
            "Spicy": "q3_mexican_dish",
            "Mild": "q3_mexican_dish"
        }
    },
    "q2_indian_dish": {
        "question": "Great choice! Which Indian dish sounds good?",
        "options": ["Curry", "Biryani", "Naan with Dal"],
        "next_question_map": {
            "Curry": "end",
            "Biryani": "end",
            "Naan with Dal": "end"
        }
    },
    "q3_pasta_sauce": {
        "question": "Which pasta sauce would you prefer?",
        "options": ["Marinara", "Alfredo", "Pesto"],
        "next_question_map": {
            "Marinara": "end",
            "Alfredo": "end",
            "Pesto": "end"
        }
    },
    "q3_pizza_toppings": {
        "question": "Any specific pizza toppings in mind?",
        "options": ["Pepperoni", "Mushrooms", "Vegetables"],
        "next_question_map": {
            "Pepperoni": "end",
            "Mushrooms": "end",
            "Vegetables": "end"
        }
    },
    "q3_mexican_dish": {
        "question": "What kind of Mexican dish are you thinking of?",
        "options": ["Tacos", "Burritos", "Enchiladas"],
        "next_question_map": {
            "Tacos": "end",
            "Burritos": "end",
            "Enchiladas": "end"
        }
    }
}

# --- Chat Endpoint ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles the chatbot conversation.
    Send user_input and conversation_history to progress the chat.
    """
    current_history = request.conversation_history
    user_input = request.user_input

    # Determine the current state of the conversation
    last_question_id = None
    last_answer = None
    if current_history:
        last_entry = current_history[-1]
        last_question_id = last_entry.question_id
        last_answer = last_entry.answer

    # Determine the next question ID based on the last answer
    next_question_id = "q1_food_type"  # Default for starting the conversation

    if last_question_id and last_answer:
        # If there's previous history, find the next question based on the last answer
        prev_question_config = QUESTIONS.get(last_question_id)
        if prev_question_config and "next_question_map" in prev_question_config:
            next_question_id = prev_question_config["next_question_map"].get(last_answer)
            if next_question_id is None:
                # This should ideally not happen if options and maps are correctly defined
                raise HTTPException(status_code=400, detail="Invalid state: Could not determine next question.")

    # Process user input if provided (i.e., not the very first request)
    if user_input is not None:
        # Validate user_input against options of the question that was just asked
        # This assumes the user_input is an answer to the 'last_question_id'
        if last_question_id and last_question_id in QUESTIONS:
            expected_options = QUESTIONS[last_question_id].get("options", [])
            if user_input not in expected_options:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid input for '{QUESTIONS[last_question_id]['question']}': '{user_input}'. "
                           f"Please choose from {', '.join(expected_options)}."
                )
            # Add the user's valid answer to the history
            current_history.append(
                ConversationEntry(question_id=last_question_id, answer=user_input)
            )
            # Update next_question_id based on the *newly added* answer
            next_question_config = QUESTIONS.get(last_question_id)
            if next_question_config and "next_question_map" in next_question_config:
                next_question_id = next_question_config["next_question_map"].get(user_input)
            else:
                # This path should be handled if the last question was an 'end' point
                next_question_id = "end"
        elif not current_history:
            # This handles the very first request where user_input might be sent
            # but no question has been asked yet. It should ideally be empty.
            # For simplicity, we'll let the first question be asked.
            pass

    # Prepare the response based on the determined next_question_id
    if next_question_id == "end":
        # Conversation is complete
        final_summary = {entry.question_id: entry.answer for entry in current_history}
        return ChatResponse(
            message="Thank you for your responses! Here's a summary of your preferences:",
            question_id=None,
            options=None,
            conversation_history=current_history,
            is_conversation_complete=True,
            final_summary=final_summary
        )
    elif next_question_id in QUESTIONS:
        # Ask the next question
        next_question_config = QUESTIONS[next_question_id]
        return ChatResponse(
            message=next_question_config["question"],
            question_id=next_question_id,
            options=next_question_config["options"],
            conversation_history=current_history,
            is_conversation_complete=False,
            final_summary=None
        )
    else:
        # This state should ideally not be reached if logic is sound
        raise HTTPException(status_code=500, detail="Chatbot internal error: Could not find next question.")
