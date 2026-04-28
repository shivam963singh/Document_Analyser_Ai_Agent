import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai   # ✅ new package
from document_parser import extract_text

def main():
    parser = argparse.ArgumentParser(description="Document Analysis Agent")
    parser.add_argument("file_path", type=str, help="Path to the document (PDF, DOCX, XLSX, IPYNB, etc.)")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set properly.", file=sys.stderr)
        sys.exit(1)

    # ✅ Create client with API key
    client = genai.Client(api_key=api_key)

    print(f"Reading file: {args.file_path} ...")
    try:
        document_text = extract_text(args.file_path)
    except Exception as e:
        print(f"Error reading document: {e}", file=sys.stderr)
        sys.exit(1)

    if not document_text.strip():
        print("Warning: The document appears to be empty or text could not be extracted.")
        sys.exit(1)

    print("Document successfully read. Initializing Gemini agent...")

    # We will use gemini-2.5-flash which is the recommended model and works well with the SDK
    model_id = "gemini-2.5-flash"

    print("\nGenerating document summary...\n" + "-"*40)

    summary_prompt = f"""
    You are an expert Document Analysis Agent. 
    Below is the text extracted from a document. Please provide a comprehensive summary of the document.

    Document Text:
    {document_text}
    """

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=summary_prompt
        )
        print(response.text)
        print("-" * 40)
    except Exception as e:
        print(f"Failed to generate summary: {e}")

    print("\nAgent is ready! You can now ask questions about the document.")
    print("Type 'quit' or 'exit' to stop.\n")

    # ✅ Interactive Q&A loop using `client.chats.create`
    try:
        chat = client.chats.create(
            model=model_id,
            history=[
                {
                    "role": "user",
                    "parts": [{"text": f"Here is a document for context. I will ask you questions about it.\n\nDocument Text:\n{document_text}"}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "I have received the document and generated the summary. I am ready to answer any questions you have."}]
                }
            ]
        )
    except Exception as e:
        print(f"Failed to initialize chat: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            if not user_input.strip():
                continue

            response = chat.send_message(user_input)
            print(f"\nAgent: {response.text}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
