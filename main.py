# main.py
import streamlit as st
import requests
import os
import re
from utils.huggingface_client import generate_response, generate_practice

# Set up page configuration
st.set_page_config(
    page_title="PythonPal - Learn Python with AI!",
    page_icon="🐍",
    layout="wide"
)

# Inject custom CSS for a playful, kid-friendly UI with a black theme.
# Updated CSS includes a rule to force the chat input text color to white.
st.markdown(
    """
    <style>
    /* Overall page background */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #000000 100%);
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #000000 0%, #c2e9fb 100%);
        color: #ffffff;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-shadow: 1px 1px 2px #555;
        color: #ffffff;
    }
    /* Chat message styling */
    .stMarkdown p {
        font-size: 1.1rem;
        line-height: 1.5;
        color: #ffffff;
    }
    /* Chat bubble enhancements */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    /* Button styling and hover fix */
    .stButton>button {
        background-color: #ff5733;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 8px 16px;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e04e2d;
        color: white !important;
    }
    /* Practice session text area styling */
    textarea {
        border-radius: 10px !important;
        border: 2px solid #ffffff !important;
        padding: 10px;
        font-size: 1.1rem;
        color: #ffffff !important;
    }
    /* Chat input styling: force input text color to white and a dark background */
    div[data-testid="stTextInput"] input {
        color: #ffffff !important;
        background-color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_valid" not in st.session_state:
    st.session_state.api_valid = False
if "current_character" not in st.session_state:
    st.session_state.current_character = None
if "practice" not in st.session_state:
    st.session_state.practice = None
if "chocolates" not in st.session_state:
    st.session_state.chocolates = 0
if "current_concept" not in st.session_state:
    st.session_state.current_concept = "Introduction to Python"
if "asked_practice_questions" not in st.session_state:
    st.session_state.asked_practice_questions = []

# Sidebar configuration
with st.sidebar:
    st.title("🔧 Settings")
    hf_key = st.text_input("Enter Hugging Face API Key:", type="password")
    st.info(
        "You can get your Hugging Face API key from [Hugging Face Tokens](https://huggingface.co/settings/tokens). "
        "Simply sign up and create a new token."
    )
    character = st.selectbox("Choose your tutor:", 
                           ["Friendly Robot 🤖", "Magic Dragon 🐉", "Super Coder 🦸"],
                           index=0)
    
    # Display chocolate counter with a fun emoji
    st.markdown(f"🍫 **Chocolates Earned:** {st.session_state.chocolates}")
    
    # Reset chat if character changes
    if st.session_state.current_character != character:
        st.session_state.messages = []
        st.session_state.current_character = character
        st.session_state.practice = None
        st.session_state.current_concept = "Introduction to Python"
    
    st.markdown("---")
    st.markdown("Made with ❤️ by Parth Verma")

# Character configurations
characters = {
    "Friendly Robot 🤖": {
        "emoji": "🤖",
        "color": "blue",
        "intro": "Hi! I'm Robo-Tutor! 🤖\nLet's learn Python basics step-by-step!",
        "style": "Give clear, simple explanations with real-world examples kids understand",
        "practice": "Create basic coding challenges about the current concept"
    },
    "Magic Dragon 🐉": {
        "emoji": "🐉",
        "color": "green",
        "intro": "Greetings young coder! 🐉\nLet's learn Python through magical stories!",
        "style": "Explain concepts using fantasy stories and adventure metaphors",
        "practice": "Create story-based coding challenges"
    },
    "Super Coder 🦸": {
        "emoji": "🦸",
        "color": "red",
        "intro": "Welcome to Code Academy! 🦸\nLet's solve real coding challenges!",
        "style": "Ask questions and wait for correct answers, provide detailed feedback",
        "practice": "Create problem-solving scenarios with expected answers"
    }
}

# Home page content (landing page)
def show_home():
    # Create three columns (left, center, right) to center the landing page content.
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #ff5733;'>Welcome to PythonPal! 🎉</h1>", unsafe_allow_html=True)
        # Centered and resized image using HTML
        st.markdown(
            "<div style='display: flex; justify-content: center;'>"
          # "<img src='assets/logo.png' width='150'>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            ## What is PythonPal?
            
            **PythonPal** is an AI-powered Python tutor designed especially for kids. Our application makes learning Python fun and interactive by combining clear explanations, real-world examples, and engaging coding challenges. Whether you're just starting out or want to test your skills, PythonPal adapts to your learning pace and provides instant feedback.
            
            **Unique Features:**
            - **Interactive Lessons:** Ask questions and get immediate, kid-friendly answers.
            - **Practice Assessments:** Every correct answer in your practice assessments rewards you with a virtual chocolate 🍫 and even a celebratory balloon animation!
            - **Personalized Experience:** Choose from three unique tutor characters, each with their own teaching style.
            
            ### Meet Your Tutors:
            
            - **Friendly Robot 🤖:** Explains Python concepts in a simple, straightforward way using everyday examples.
            - **Magic Dragon 🐉:** Uses enchanting stories and adventures to make complex ideas easier to understand.
            - **Super Coder 🦸:** Challenges you with fun assignments and coding puzzles to test your knowledge.
            
            Every correct answer during practice not only boosts your confidence but also earns you a chocolate reward, making learning a sweet experience!
            
            ### Get Started:
            1. Enter your **Hugging Face API key** in the sidebar. (If your API key runs out of quota, simply update it here.)
            2. Choose your favorite tutor.
            3. Ask a question or dive straight into an interactive lesson!
            """, unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# Validate API key
if hf_key or 'HUGGINGFACE_TOKEN' in os.environ:
    st.session_state.api_valid = True
else:
    st.warning("⚠️ Please enter your Hugging Face API key in the sidebar")
    show_home()
    st.stop()

def clean_code(s):
    """
    Remove markdown formatting (like backticks and code blocks)
    and normalize whitespace and case.
    """
    s = re.sub(r"```(?:python)?\s*", "", s)
    s = re.sub(r"```", "", s)
    s = re.sub(r"`", "", s)
    return s.strip().lower()

def handle_practice_answer(answer, correct_answer, clear_session=False):
    user_ans = clean_code(answer)
    acceptable_answers = []
    
    if isinstance(correct_answer, list):
        acceptable_answers = [clean_code(str(ans)) for ans in correct_answer]
    elif isinstance(correct_answer, str):
        try:
            parsed = eval(correct_answer)
            if isinstance(parsed, list):
                acceptable_answers = [clean_code(str(ans)) for ans in parsed]
            else:
                raise ValueError
        except:
            acceptable_answers = [clean_code(ans) for ans in re.split(r',|/| or ', correct_answer)]
    else:
        acceptable_answers = [clean_code(str(correct_answer))]

    acceptable_answers.append(clean_code(str(correct_answer)))
    
    if user_ans in acceptable_answers:
        st.session_state.chocolates += 1
        st.success("🎉 Correct! You earned a chocolate! 🍫")
        st.balloons()  # Celebrate with balloons!
        if clear_session:
            st.session_state.practice = None
    else:
        st.error(
            f"Oops! Let's try again. One acceptable answer is:\n```python\n{correct_answer}\n```"
        )
        if clear_session:
            st.session_state.practice = None

# Main app logic
def main():
    if not st.session_state.api_valid:
        show_home()
        return

    selected_char = characters[character]
    
    # Add character introduction if no messages yet
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant",
            "content": selected_char["intro"],
            "avatar": selected_char["emoji"]
        })

    # Chat interface header (centered)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.title(f"PythonPal {selected_char['emoji']}")
    st.caption(f"Your {character} is ready to help you learn Python!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])
    
    # Practice session handling (with updated Replit link and two buttons)
    if st.session_state.practice:
        with st.chat_message("assistant", avatar=selected_char["emoji"]):
            st.markdown(
                f"**Practice Time!** 🏆\n\n"
                f"{st.session_state.practice['question']}\n\n"
                f"**Tip:** You can use the [Python Editor](https://replit.com/~) to test your code."
            )
            answer = st.text_area("Write your code here:", key="practice_answer")
            col1, col2 = st.columns(2)
            # Submit Answer: validate and, if correct, clear the practice panel.
            if col1.button("Submit Answer"):
                prev_chocs = st.session_state.chocolates
                handle_practice_answer(answer, st.session_state.practice['answer'], clear_session=True)
                if st.session_state.chocolates > prev_chocs:
                    st.success("Congratulations on your correct answer!")
            # Exit to Chat Mode: evaluate (if answer provided) and clear the practice panel.
            if col2.button("Exit to Chat Mode"):
                if answer.strip() != "":
                    handle_practice_answer(answer, st.session_state.practice['answer'], clear_session=True)
                else:
                    st.session_state.practice = None
        return

    # User input handling
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "avatar": "👦"
        })
        
        with st.chat_message("user", avatar="👦"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            try:
                system_prompt = f"""You are a {character} Python tutor for children. 
{selected_char['style']}. Current concept: {st.session_state.current_concept}.
Whenever you ask for code input or provide a coding challenge, include a link to an online Python editor (for example: https://replit.com/~).
- Check if user answers are correct
- Explain errors clearly
- Keep responses under 100 words
- Use {selected_char['emoji']} emojis occasionally"""
                
                response = generate_response(
                    api_key=hf_key or os.environ.get('HUGGINGFACE_TOKEN'),
                    system_message=system_prompt,
                    conversation_history=st.session_state.messages,
                    character=character
                )
                
                concept_match = re.search(r'Current concept: (.+?)\.', response)
                if concept_match:
                    st.session_state.current_concept = concept_match.group(1)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                return
        
        with st.chat_message("assistant", avatar=selected_char["emoji"]):
            st.markdown(response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "avatar": selected_char["emoji"]
        })
                    
        # Generate practice question every 3 user messages (only if no practice session is active)
        user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
        if user_msg_count >= 3 and user_msg_count % 3 == 0 and st.session_state.practice is None:
            # Prepend a note to the concept so that the practice question is beginner-friendly.
            practice_concept = "Beginner friendly practice: " + st.session_state.current_concept
            practice_data = generate_practice(
                api_key=hf_key or os.environ.get('HUGGINGFACE_TOKEN'),
                concept=practice_concept,
                character=character
            )
            if practice_data:
                new_question = practice_data.get("question", "").strip().lower()
                if new_question and new_question not in st.session_state.asked_practice_questions:
                    st.session_state.practice = practice_data
                    st.session_state.asked_practice_questions.append(new_question)
                    st.experimental_rerun()
                else:
                    st.session_state.practice = None

if __name__ == "__main__":
    main()
