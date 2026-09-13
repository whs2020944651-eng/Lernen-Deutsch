import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


# 加載環境變量 (保護 API Key 不被泄露)
load_dotenv()


def main():
    print("🇩🇪 Willkommen bei Lernen-Deutsch CLI! (Welcome to Lernen-Deutsch CLI)")
    print("输入 'exit' 或 'quit' 结束对话。\n")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: 未找到 OPENAI_API_KEY。")
        print("出于安全考虑，请在 .env 文件中设置您的 API Key，不要硬编码在代码中。")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # 定义 Agent 行为规范，呼应申请表中的 Prompt 设置
    system_prompt = """You are a helpful and strict German language tutor.
    1. Correct any German grammar or spelling mistakes the user makes.
    2. Explain the correction briefly in Chinese or English.
    3. Continue the conversation naturally in German to encourage practice."""

    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("Du (You): ")
        if user_input.lower() in ["exit", "quit"]:
            print("Tschüss! (Goodbye!)")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
            )

            reply = response.choices[0].message.content
            print(f"\nKI Tutor: {reply}\n")
            messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"Agent Error: {e}")


if __name__ == "__main__":
    main()