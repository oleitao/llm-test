import os
import pandas as pd
from dotenv import load_dotenv
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry

load_dotenv()

db_path = os.getenv("LANCEDB_PATH")
table_name = os.getenv("LANCEDB_TABLE")

model = get_registry().get("sentence-transformers").create(name="all-mpnet-base-v2")

class TweetDocument(LanceModel):
    tweet_count: int
    tweet_id: int
    username: str
    text: str = model.SourceField()
    created_at: str
    url: str
    vector: Vector(model.ndims()) = model.VectorField()

db = lancedb.connect(db_path)
model = get_registry().get("sentence-transformers").create(name="all-mpnet-base-v2")

def initialize_database():
    db = lancedb.connect(db_path)
    
    # Debug: Print available tables
    existing_tables = db.table_names()
    print(f"Existing tables: {existing_tables}")

    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists. Opening...")
        try:
            tbl = db.open_table(table_name)
            print(f"Successfully opened table '{table_name}' with {len(tbl)} rows")
            return tbl
        except Exception as e:
            print(f"Error opening existing table: {str(e)}")
            print("Dropping table and recreating...")
            db.drop_table(table_name)
    
    print("Creating new table...")
    try:
        # Try to read CSV with different encodings
        try:
            tweets_df = pd.read_csv("data/elonmusk_tweets.csv", encoding='utf-8')
        except UnicodeDecodeError:
            tweets_df = pd.read_csv("data/elonmusk_tweets.csv", encoding='latin-1')
        
        print(f"Loaded CSV with {len(tweets_df)} rows")
        print(f"CSV columns: {tweets_df.columns.tolist()}")
        
        # Clean the data and handle missing URLs
        def clean_text(text):
            if pd.isna(text):
                return ""
            return str(text).replace('\xa0', ' ').replace('\u00a0', ' ').strip()
        
        # Apply text cleaning
        tweets_df['text'] = tweets_df['text'].apply(clean_text)
        tweets_df['username'] = tweets_df['username'].apply(clean_text)
        
        # Generate URL if missing
        if 'url' not in tweets_df.columns:
            tweets_df['url'] = tweets_df.apply(
                lambda row: f"https://twitter.com/{row['username']}/status/{row['tweet_id']}" 
                if pd.notna(row.get('tweet_id')) and pd.notna(row.get('username')) 
                else "", axis=1
            )
        
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
        
        print(f"Prepared {len(data)} records for insertion")

        table = db.create_table(table_name, schema=TweetDocument)
        table.add(data)
        table.create_fts_index("text")

        print(f"Table '{table_name}' created successfully with {len(table)} rows")
        return table
        
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        raise