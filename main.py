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
import vocab_db

# Load environment variables
load_dotenv()

# Database setup
DB_PATH = "vocabulary.db"


def init_database(db_path=DB_PATH):
    """Initialize SQLite database for vocabulary management and conversations."""
    vocab_db.init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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


def add_vocabulary(word, translation, part_of_speech="", example="", db_path=DB_PATH):
    """Add or update vocabulary word in database."""
    return vocab_db.add_word(
        word=word,
        translation=translation,
        part_of_speech=part_of_speech,
        example=example,
        db_path=db_path,
    )


def get_vocabulary_list(limit=10, db_path=DB_PATH):
    """Retrieve vocabulary words from database."""
    words = vocab_db.list_words(limit=limit, sort_by="frequency", db_path=db_path)
    return [(w["word"], w["translation"], w.get("frequency", 1)) for w in words]


def get_vocabulary_stats(db_path=DB_PATH):
    """Get vocabulary statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    total_words = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversation_history")
    total_conversations = cursor.fetchone()[0]
    
    conn.close()
    return total_words, total_conversations


def save_conversation(user_message, assistant_response, db_path=DB_PATH):
    """Save conversation to database for learning history."""
    conn = sqlite3.connect(db_path)
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
  4. Type 'vocab' or 'vocab list' to see your learned words
  5. Type 'vocab add [word] [translation]' to add words directly
  6. Type 'vocab review' to practice spaced repetition
  7. Type 'vocab export' to export vocabulary to CSV
  8. Type 'stats' to view your progress
  9. Type 'exit' or 'quit' to finish

📖 COMMANDS:
  • 'vocab'                           - Show your learned vocabulary (top 10)
  • 'vocab add <word> <translation>'  - Add new vocabulary word
  • 'vocab review'                    - Practice vocabulary via spaced repetition
  • 'vocab export [file.csv]'         - Export vocabulary as CSV file
  • 'stats'                           - Display learning statistics
  • 'exit'                            - End the session
  • 'quit'                            - End the session

💡 TIPS:
  ✓ Don't worry about mistakes - that's how you learn!
  ✓ Try to write complete sentences
  ✓ Ask questions if you don't understand
  ✓ Practice daily for best results
  ✓ Your progress is automatically saved

─────────────────────────────────────────────────────────────────
"""
    print(welcome_text)


def handle_vocab_command(command_str, db_path=DB_PATH):
    """
    Handle vocabulary management subcommands.
    Returns True if handled, False otherwise.
    """
    parts = command_str.strip().split()
    if not parts or parts[0].lower() != "vocab":
        return False

    subcommand = parts[1].lower() if len(parts) > 1 else "list"

    if subcommand in ["list", "show"]:
        limit = 10
        if len(parts) > 2 and parts[2].isdigit():
            limit = int(parts[2])
        words = get_vocabulary_list(limit=limit, db_path=db_path)
        if words:
            print(f"\n📖 Your Learned Vocabulary (Top {len(words)}):")
            for i, (word, translation, freq) in enumerate(words, 1):
                print(f"  {i}. {word} ({translation}) - Frequency: {freq}")
            print()
        else:
            print("\n📖 No vocabulary learned yet. Keep practicing!\n")
        return True

    elif subcommand == "add":
        if len(parts) < 4:
            print("\n❌ Usage: vocab add <word> <translation> [difficulty]\n")
            return True
        word = parts[2]
        translation = parts[3]
        difficulty = parts[4] if len(parts) > 4 else "medium"
        entry = add_vocabulary(word, translation, db_path=db_path)
        vocab_db.update_word(word, difficulty=difficulty, db_path=db_path)
        print(f"\n✅ Added '{word}' ({translation}) [Difficulty: {difficulty}] to vocabulary!\n")
        return True

    elif subcommand == "review":
        words_to_review = vocab_db.get_words_for_review(limit=5, db_path=db_path)
        if not words_to_review:
            print("\n📖 No vocabulary available to review. Add words with 'vocab add' first!\n")
            return True

        print(f"\n🧠 Spaced Repetition Review ({len(words_to_review)} words):")
        print("──────────────────────────────────────────────────")
        for i, item in enumerate(words_to_review, 1):
            target_word = item["word"]
            expected = item["translation"].strip().lower()
            diff = item.get("difficulty", "medium")
            print(f"[{i}/{len(words_to_review)}] What is the translation of: '{target_word}' (Difficulty: {diff})?")
            try:
                ans = input("   Your translation: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nReview cancelled.\n")
                return True

            is_correct = ans.lower() == expected
            vocab_db.record_review(target_word, success=is_correct, db_path=db_path)
            if is_correct:
                print(f"   ✅ Correct! ('{target_word}' = '{item['translation']}')\n")
            else:
                print(f"   ❌ Incorrect. Expected: '{item['translation']}'. We will review this again soon!\n")

        print("🎉 Review session complete!\n")
        return True

    elif subcommand == "export":
        export_file = parts[2] if len(parts) > 2 else "vocabulary_export.csv"
        path = vocab_db.export_csv(file_path=export_file, db_path=db_path)
        print(f"\n📁 Vocabulary exported successfully to: {path}\n")
        return True

    else:
        print(f"\n❌ Unknown vocab command: {subcommand}. Available: list, add, review, export\n")
        return True


def main():
    """Main entry point for the tutoring agent."""
    # Support standalone CLI execution of vocabulary commands without requiring API key
    if len(sys.argv) > 1 and sys.argv[1].lower() == "vocab":
        init_database()
        handle_vocab_command(" ".join(sys.argv[1:]))
        return

    # Check API key for chat session
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=your-key-here")
        print("\nNote: You can still run vocabulary CLI commands offline:")
        print("  python main.py vocab add <word> <translation>")
        print("  python main.py vocab review")
        print("  python main.py vocab export")
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
            
            # Handle vocab commands (e.g. 'vocab', 'vocab add ...', 'vocab review', 'vocab export')
            if user_input.lower().startswith("vocab"):
                handle_vocab_command(user_input)
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
