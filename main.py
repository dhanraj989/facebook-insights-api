import os
import requests
import asyncio
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from playwright.sync_api import sync_playwright
from google.cloud import storage, firestore
from pydantic import BaseModel
from typing import List, Optional
import groq
import subprocess
import json

# Load Google Cloud Credentials
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if google_credentials_json:
    credentials_path = "/tmp/gcp_credentials.json"
    with open(credentials_path, "w") as f:
        f.write(google_credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# FastAPI App Initialization
app = FastAPI()

# Firestore Database
DB_NAME = "facebookinsights"
firestore_client = firestore.Client()

# Google Cloud Storage (GCS) Setup
GCS_BUCKET = "facebook-insights-bucket"
gcs_client = storage.Client()
bucket = gcs_client.bucket(GCS_BUCKET)

# Groq API Key for AI-based summaries
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = groq.Client(api_key=GROQ_API_KEY)

# Pydantic Model for Page Data
class Page(BaseModel):
    username: str
    page_name: str
    page_url: str
    profile_pic: Optional[str]
    email: Optional[str]
    website: Optional[str]
    category: Optional[str]
    followers: int
    likes: int
    creation_date: Optional[str]
    posts: Optional[List[dict]]
    followers_list: Optional[List[dict]]

# Upload images to Google Cloud Storage (GCS)
def upload_to_gcs(file_url, destination_blob_name):
    response = requests.get(file_url)
    if response.status_code == 200:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(response.content, content_type="image/jpeg")
        return f"https://storage.googleapis.com/{GCS_BUCKET}/{destination_blob_name}"
    return None

# Scraper Function
def scrape_facebook_page(username: str):
    try:
        result = subprocess.run(
            ["python", "scraper.py", username],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except Exception:
        return {}

# Store Data in Firestore
def store_page_data(username, data):
    page_ref = firestore_client.collection(DB_NAME).document(username)
    page_ref.set(data)

# Root Route
@app.get("/")
async def root():
    return {"message": "Welcome to Facebook Insights API!"}

# Fetch Page Details
@app.get("/page/{username}")
def get_page_details(username: str, background_tasks: BackgroundTasks):
    page_ref = firestore_client.collection(DB_NAME).document(username)
    page_doc = page_ref.get()

    print(f"🔍 Checking Firestore for {username}")

    if not page_doc.exists:
        print("🚀 Scraping Data (Not in Firestore)")
        page_data = scrape_facebook_page(username)
        print(f"📌 Scraped Data: {page_data}")

        if page_data:  # Store only if valid data
            background_tasks.add_task(store_page_data, username, page_data)
        else:
            print("⚠️ Scraping returned empty data")
    else:
        print("✅ Found in Firestore")
        page_data = page_doc.to_dict()

    return page_data

# Search Pages with Filters & Pagination
@app.get("/pages")
async def search_pages(
    min_followers: Optional[int] = Query(0), 
    max_followers: Optional[int] = Query(1_000_000),
    category: Optional[str] = Query(None),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit")
):
    query = firestore_client.collection(DB_NAME).where("followers", ">=", min_followers).where("followers", "<=", max_followers)

    if category:
        query = query.where("category", "==", category)

    pages = query.offset((page - 1) * limit).limit(limit).stream()
    page_list = [page.to_dict() for page in pages]

    return {"total": len(page_list), "page": page, "pages": page_list}

# AI-Generated Summary for a Page
@app.get("/page/{username}/summary")
async def get_page_summary(username: str):
    page_ref = firestore_client.collection(DB_NAME).document(username)
    page_doc = page_ref.get()

    if not page_doc.exists():
        raise HTTPException(status_code=404, detail="Page not found")

    page_data = page_doc.to_dict()

    prompt = f"Generate a short business summary for a Facebook page named '{page_data['page_name']}' with {page_data['followers']} followers in the '{page_data['category']}' category."
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": prompt}]
    )

    return {"summary": response.choices[0].message.content}

# Run the FastAPI Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
