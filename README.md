# **Facebook Insights API**  

This project is a **FastAPI-based web service** that scrapes Facebook pages and provides useful insights like followers, likes, and other details. The API stores data in **Google Firestore** and uploads media files to **Google Cloud Storage (GCS)**.  

## **Project Structure**  

### **1. `main.py`**  
This is the main file that runs the **FastAPI server**. It handles requests and responses for getting Facebook page details, searching for pages, and generating AI-based summaries.  

#### **Key Features of `main.py`:**  
✅ Fetches Facebook page details either from **Firestore** or by scraping (if not already stored).  
✅ Saves and retrieves data from **Google Firestore**.  
✅ Uploads profile pictures or other images to **Google Cloud Storage (GCS)**.  
✅ Generates AI-based summaries for a page using **Groq API**.  

#### **Endpoints in `main.py`:**  

| Method | Endpoint | Description |  
|--------|----------|-------------|  
| `GET` | `/` | Basic API welcome message. |  
| `GET` | `/page/{username}` | Fetches details of a given Facebook page. |  
| `GET` | `/pages` | Searches pages with filters like followers and category. |  
| `GET` | `/page/{username}/summary` | Generates an AI-based summary for a page. |  

---

### **2. `scraper.py`**  
This is a **Python script** that scrapes data from Facebook pages using **Playwright**.  

#### **How it Works:**  
1. It opens a browser using **Playwright** and navigates to the given Facebook page.  
2. It extracts information like **page name, followers, likes, category, email, and website**.  
3. It returns the extracted data as **JSON**.  

#### **What It Scrapes:**  
- Page Name  
- Page URL  
- Profile Picture  
- Email (if available)  
- Website (if available)  
- Category  
- Number of Followers & Likes  

---

## **How to Run the Project**  

### **1. Install Dependencies:**  
Make sure you have **Python 3.8+** installed. Then install the required packages:  
```bash
pip install -r requirements.txt
playwright install
```

### **2. Run the FastAPI Server:**  
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be accessible at:  
👉 `http://localhost:8000`  

### **3. Run the Scraper Separately (Optional)**  
If you want to test the scraper manually, run:  
```bash
python scraper.py <facebook_page_username>
```

---

## **Contributors**  
👤 **Dhanraj Malla** - Developer  

---  
