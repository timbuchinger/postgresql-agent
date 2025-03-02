#!/usr/bin/env python3
import sys

from dotenv import load_dotenv

from postgresql_agent import PostgresConnector, answer_database_question


def main():
    # Load environment variables
    load_dotenv()

    try:
        # Initialize database connection
        print("Initializing database connection...")
        db = PostgresConnector()

        # Interactive loop
        while True:
            # Get question from user
            print("\nEnter your question (or 'quit' to exit):")
            question = input("> ")

            if question.lower() in ["quit", "exit", "q"]:
                break

            try:
                # Process question and get answer
                print("\nProcessing question...")
                answer = answer_database_question(question)
                print("\nAnswer:", answer)
            except Exception as e:
                print(f"\nError processing question: {str(e)}")

    except Exception as e:
        print(f"Failed to initialize: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
