import os
import pandas as pd
from dotenv import load_dotenv
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pathlib import Path
import sys

load_dotenv()

db_path_str = os.getenv("LANCEDB_PATH", "data/lancedb")
table_name = os.getenv("LANCEDB_TABLE", "tweets")

# Convert string path to Path object
db_path = Path(db_path_str)

# Verify sentence-transformers is installed
try:
    # Try to import before proceeding
    import sentence_transformers
    print("Successfully imported sentence_transformers module")
except ImportError:
    print("ERROR: sentence-transformers package not found!")
    print("Please install it with: pip install sentence-transformers==2.2.2")
    sys.exit(1)

try:
    model = get_registry().get("sentence-transformers").create(name="all-mpnet-base-v2")
except Exception as e:
    print(f"ERROR initializing sentence-transformers model: {str(e)}")
    print("This could be because sentence-transformers is not correctly installed.")
    print("Try running: pip install -U sentence-transformers==2.2.2")
    raise

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
            csv_path = get_resource_path("data/fabrizioromano_tweets.csv")
            print(f"Loading data from: {csv_path}")
            
            tweets_df = pd.read_csv(csv_path)
            data = tweets_df.apply(
                lambda row: {
                    "tweet_count": row["tweet_count"],
                    "tweet_id": row["tweet_id"],
                    "username": row["username"],
                    "text": row["text"],
                    "created_at": row["created at"],
                    "url": row["url"]
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
                "data/fabrizioromano_tweets.csv", 
                "/app/data/fabrizioromano_tweets.csv",
                "../data/fabrizioromano_tweets.csv"
            ]:
                if os.path.exists(path):
                    print(f"Found at: {path}")
            
            raise
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise