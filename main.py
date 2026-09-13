"""
Lernen-Deutsch - German Language Learning AI Agent

A CLI-based interactive platform for learning German through conversational AI.
Powered by OpenAI's language models with real-time corrections and explanations.
Features SQLite database for vocabulary management and progress tracking.
"""

import os
import sqlite3
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Database setup
DB_PATH = "vocabulary.db"


def init_database():
    """Initialize SQLite database for vocabulary management."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            translation TEXT NOT NULL,
            part_of_speech TEXT,
            example TEXT,
            frequency INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            word_count INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_conversations INTEGER DEFAULT 0,
            total_words_learned INTEGER DEFAULT 0,
            accuracy_score REAL DEFAULT 0.0,
            last_session TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def add_vocabulary(word, translation, part_of_speech="", example=""):
    """Add or update vocabulary word in database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO vocabulary (word, translation, part_of_speech, example)
            VALUES (?, ?, ?, ?)
        """, (word, translation, part_of_speech, example))
    except sqlite3.IntegrityError:
        # Word already exists, update frequency
        cursor.execute("""
            UPDATE vocabulary 
            SET frequency = frequency + 1, updated_at = CURRENT_TIMESTAMP
            WHERE word = ?
        """, (word,))
    
    conn.commit()
    conn.close()


def get_vocabulary_list(limit=10):
    """Retrieve vocabulary words from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT word, translation, frequency 
        FROM vocabulary 
        ORDER BY frequency DESC 
        LIMIT ?
    """, (limit,))
    words = cursor.fetchall()
    conn.close()
    
    return words


def get_vocabulary_stats():
    """Get vocabulary statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total_words = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversation_history")
    total_conversations = cursor.fetchone()[0]
    
    conn.close()
    
    return total_words, total_conversations


def save_conversation(user_message, assistant_response):
    """Save conversation to database for learning history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    word_count = len(user_message.split())
    cursor.execute("""
        INSERT INTO conversation_history (user_message, assistant_response, word_count)
        VALUES (?, ?, ?)
    """, (user_message, assistant_response, word_count))
    
    conn.commit()
    conn.close()


def display_welcome():
    """Display welcome screen with usage information."""
    welcome_text = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          🇩🇪 LERNEN-DEUTSCH 🇩🇪                               ║
║                                                                ║
║     German Language Learning with AI Tutoring Support         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📚 FEATURES:
  • Interactive German conversations with AI feedback
  • Real-time grammar and spelling corrections
  • Vocabulary tracking and database management
  • Conversation history for review and progress
  • Multi-language explanations (German, English, Chinese)
  • Progress tracking and statistics

🎯 HOW TO USE:
  1. Type in German - any level is welcome!
  2. Get immediate corrections and explanations
  3. Continue practicing to improve your skills
  4. Type 'vocab' to see your learned words
  5. Type 'stats' to view your progress
  6. Type 'exit' or 'quit' to finish

📖 COMMANDS:
  • 'vocab'  - Show your learned vocabulary (top 10)
  • 'stats'  - Display learning statistics
  • 'exit'   - End the session
  • 'quit'   - End the session

💡 TIPS:
  ✓ Don't worry about mistakes - that's how you learn!
  ✓ Try to write complete sentences
  ✓ Ask questions if you don't understand
  ✓ Practice daily for best results
  ✓ Your progress is automatically saved

─────────────────────────────────────────────────────────────────
"""
    print(welcome_text)


def main():
    """Main entry point for the tutoring agent."""
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Initialize database
    init_database()
    
    # Display welcome screen
    display_welcome()
    
    # Define system prompt
    system_prompt = """You are a helpful and strict German language tutor.
    
Your responsibilities:
1. Correct any German grammar or spelling mistakes the user makes
2. Explain the correction briefly in Chinese or English
3. Continue the conversation naturally in German to encourage practice
4. Provide pronunciation guidance when helpful
5. Use simple, clear German appropriate for learners

Always be encouraging while maintaining high standards.
Format corrections clearly so the user can learn from their mistakes."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Main conversation loop
    while True:
        try:
            user_input = input("Du (You): ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ["exit", "quit"]:
                print("\nAuf Wiedersehen! Bis zum nächsten Mal! 👋")
                break
            
            if user_input.lower() == "vocab":
                words = get_vocabulary_list()
                if words:
                    print("\n📖 Your Learned Vocabulary (Top 10):")
                    for i, (word, translation, freq) in enumerate(words, 1):
                        print(f"  {i}. {word} ({translation}) - Frequency: {freq}")
                    print()
                else:
                    print("\n📖 No vocabulary learned yet. Keep practicing!\n")
                continue
            
            if user_input.lower() == "stats":
                total_words, total_convs = get_vocabulary_stats()
                print(f"\n📊 Your Learning Statistics:")
                print(f"  • Total Words Learned: {total_words}")
                print(f"  • Total Conversations: {total_convs}")
                print()
                continue
            
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                assistant_message = response.choices[0].message.content
                
                # Add assistant response to history
                messages.append({"role": "assistant", "content": assistant_message})
                
                # Save to database
                save_conversation(user_input, assistant_message)
                
                print(f"\n🎓 Tutor: {assistant_message}\n")
                
                # Keep conversation history manageable (last 10 exchanges)
                if len(messages) > 22:  # System message + 10 exchanges
                    messages = [messages[0]] + messages[-20:]
            
            except Exception as e:
                print(f"\n❌ API Error: {e}")
                print("Please check your API key and try again.\n")
        
        except KeyboardInterrupt:
            print("\n\nAuf Wiedersehen! 👋")
            break


if __name__ == "__main__":
    main()
