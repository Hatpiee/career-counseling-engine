from dotenv import load_dotenv
load_dotenv()

from services.data_loader import load_career_data
from services.vector_store import create_vector_store


def main():
    print("Loading career data...")

    documents = load_career_data()

    print(f"Loaded {len(documents)} documents")

    print("Creating vector database...")

    vector_store = create_vector_store(documents)

    print("Vector database created successfully!")


if __name__ == "__main__":
    main()