🚀 CUD Course Scraper: AI-Powered & Student-Friendly
Scrape course schedules in 2 clicks—no coding needed. Perfect for students who want to:

✅ Auto-login to the CUD portal

📅 Find classes by professor/term

📥 Export to CSV (for Excel/Google Sheets)

🌟 Why Use This?
AI does the work: A bot mimics how you browse—clicks buttons, fills forms, scrapes data.

No tech skills needed: Just enter your student ID/password.

Instant filters: See which professors teach what, when.

App Demo

🛠️ Setup (5 Minutes)

git clone https://github.com/sudofixit/scraper 
cd scraper 
pip install -r requirements.txt  

Get a free Google Gemini API Key 

Create .env file in the project folder:

ID = "20240001234"          # Auto-updates in the app   
PASSWORD = "••••••••"       # Auto-updates in the app  
GEMINI_API_KEY = "AIzaSy..."# Paste Gemini key here  
TERM = "71"                 # Auto-updates in the app  
🖥️ How to Run
Open the app:


streamlit run app.py  
In the browser:

Enter ID + password

Choose a term (e.g., "FA 2024-25")

Click "Start Scraping"

Wait 1-2 mins (watch the bot work in Chrome!)

Done! Filter courses or download CSV.

🔧 Troubleshooting
Issue	Fix
"Invalid login"	Double-check ID/password in .env
Chrome errors	Ensure Chrome is installed at C:\Program Files\Google\Chrome\...
Slow scraping	Don’t touch the automated Chrome window

⚠️ Note
For personal/educational use only.

Data accuracy depends on the CUD portal.
