import os
import pandas as pd
from dotenv import load_dotenv
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pathlib import Path

load_dotenv()

db_path_str = os.getenv("LANCEDB_PATH", "data/lancedb")
table_name = os.getenv("LANCEDB_TABLE", "tweets")

# Convert string path to Path object
db_path = Path(db_path_str)

model = get_registry().get("sentence-transformers").create(name="all-mpnet-base-v2")

class TweetDocument(LanceModel):
    tweet_count: int
    tweet_id: int
    username: str
    text: str = model.SourceField()
    created_at: str
    url: str
    vector: Vector(model.ndims()) = model.VectorField()

# Create path if it doesn't exist
os.makedirs(db_path, exist_ok=True)

# Connect with Path object
db = lancedb.connect(db_path)
model = get_registry().get("sentence-transformers").create(name="all-mpnet-base-v2")

def initialize_database():
    # Make sure the directory exists
    os.makedirs(db_path, exist_ok=True)
    
    # Connect using the Path object
    db = lancedb.connect(db_path)

    if table_name in db.table_names():
        print("Table already exists.")
        tbl = db.open_table(table_name)
    else:
        try:
            # Import our utility function
            from utils.file_utils import get_resource_path
            
            # Get absolute path for the CSV file
            csv_path = get_resource_path("data/elonmusk_tweets.csv")
            print(f"Loading data from: {csv_path}")
            
            # Try different encodings to handle special characters
            try:
                tweets_df = pd.read_csv(csv_path, encoding='utf-8')
            except UnicodeDecodeError:
                print("UTF-8 failed, trying latin-1 encoding...")
                try:
                    tweets_df = pd.read_csv(csv_path, encoding='latin-1')
                except UnicodeDecodeError:
                    print("Latin-1 failed, trying with error handling...")
                    tweets_df = pd.read_csv(csv_path, encoding='utf-8', errors='replace')
            
            # Clean text data to handle any remaining encoding issues
            def clean_text(text):
                if pd.isna(text):
                    return ""
                # Convert to string and normalize unicode
                text = str(text)
                # Replace non-breaking spaces and other problematic characters
                text = text.replace('\xa0', ' ')  # non-breaking space
                text = text.replace('\u2026', '...')  # ellipsis
                text = text.replace('\u2019', "'")  # right single quotation mark
                text = text.replace('\u201c', '"')  # left double quotation mark
                text = text.replace('\u201d', '"')  # right double quotation mark
                # Remove any remaining non-printable characters
                text = ''.join(char for char in text if char.isprintable() or char.isspace())
                return text.strip()
            
            # Apply text cleaning to all string columns
            for col in tweets_df.columns:
                if tweets_df[col].dtype == 'object':
                    tweets_df[col] = tweets_df[col].apply(clean_text)
            
            # Check what columns are available and generate URL if needed
            print(f"Available columns: {list(tweets_df.columns)}")
            
            def generate_url(row):
                """Generate Twitter URL from username and tweet_id if URL column doesn't exist"""
                if 'url' in tweets_df.columns:
                    return row['url']
                else:
                    # Generate URL from tweet_id - assuming username is consistent
                    username = row.get('username', 'elonmusk')
                    tweet_id = row.get('tweet_id', '')
                    return f"https://twitter.com/{username}/status/{tweet_id}"
            
            data = tweets_df.apply(
                lambda row: {
                    "tweet_count": row["tweet_count"],
                    "tweet_id": str(row["tweet_id"]),  # Convert to string for consistency
                    "username": row["username"],
                    "text": row["text"],
                    "created_at": row["created at"],
                    "url": generate_url(row)
                },
                axis=1
            ).tolist()

            table = db.create_table(table_name, schema=TweetDocument)
            table.add(data)
            table.create_fts_index("text")

            print("Table created and data added")
        except FileNotFoundError as e:
            print(f"CSV file not found: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Checking if file exists in alternative locations...")
            
            # Try to locate the file in different locations
            for path in [
                "data/elonmusk_tweets.csv", 
                "/app/data/elonmusk_tweets.csv",
                "../data/elonmusk_tweets.csv"
            ]:
                if os.path.exists(path):
                    print(f"Found at: {path}")
            
            raise
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise