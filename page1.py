import os
import asyncio
import csv
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

# Initialize with explicit credentials
ID = os.getenv("ID")
PASSWORD = os.getenv("PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=SecretStr(GEMINI_API_KEY)
)

browser = Browser(
    config=BrowserConfig(
        chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        headless=False
    )
)

# Task to log in and navigate to Offerings page
formatted_task = (
    "1. Go to https://cudportal.cud.ac.ae/student/login.asp\n"
    "2. Wait for login page to load\n"
    "3. Click on #username input field\n"
    f"4. Type '{ID}' into #username\n"
    "5. Click on #password input field\n"
    f"6. Type '{PASSWORD}' into #password\n"
    "7. Click on input[type='submit']\n"
    "8. Verify successful login\n"
    "9. Navigate to Offerings section\n"
    "10. Apply SEAST filter"
)

async def extract_page_data(page):
    await page.wait_for_selector("table")
    table = await page.query_selector("table")
    rows = await table.query_selector_all("tr")

    raw_data = []
    for i, row in enumerate(rows):
        cells = await row.query_selector_all("td")
        row_data = [await cell.inner_text() for cell in cells if cell]
        if row_data:
            raw_data.append(row_data)
    return raw_data

async def click_next_page(page, current):
    next_button = await page.query_selector(f"text='{current + 1}'")
    if next_button:
        await next_button.click()
        await page.wait_for_timeout(1500)
        return True
    return False

async def main():
    context = await browser.new_context()
    agent = Agent(
        task=formatted_task,
        llm=llm,
        browser=browser,
        browser_context=context
    )

    await agent.run()
    print("🔍 Getting current page...")
    page = await context.get_current_page()

    header = [
        "Course", "Course Name", "Credits", "Instructor", "Room",
        "Days", "Date", "Start Time", "End Time", "Max Enrollment", "Total Enrollment"
    ]

    all_cleaned_data = []
    current_page = 1
    total_pages = 8

    last_course_key = None

    while current_page <= total_pages:
        print(f"📄 Scraping Page {current_page}...")
        raw_data = await extract_page_data(page)

        current_course = None
        for row in raw_data:
            if len(row) == 7 and "Credits" not in row[2]:
                course_key = f"{row[0]}|{row[1]}"
                if course_key == last_course_key:
                    continue  # skip repeated course
                current_course = {
                    "code": row[0],
                    "name": row[1],
                    "credits": row[2],
                    "start_date": row[3],
                    "end_date": row[4],
                    "max": row[5],
                    "total": row[6]
                }
                last_course_key = course_key

            elif current_course and any("Instructor" in item for item in row):
                long_cell = row[0]
                if "\n" in long_cell:
                    session_lines = long_cell.strip().split("\n")
                    for line in session_lines:
                        if "\t" in line and "Instructor" not in line:
                            parts = line.strip().split("\t")
                            if len(parts) >= 8:
                                all_cleaned_data.append([
                                    current_course["code"],
                                    current_course["name"],
                                    current_course["credits"],
                                    parts[0],  # Instructor
                                    parts[1],  # Room
                                    parts[2],  # Days
                                    parts[3],  # Date
                                    parts[4],  # Start Time
                                    parts[5],  # End Time
                                    parts[6],  # Max Enrollment
                                    parts[7]   # Total Enrollment
                                ])

        if current_page < total_pages:
            success = await click_next_page(page, current_page)
            if not success:
                print("❌ Couldn't click next page. Stopping.")
                break
        current_page += 1

    with open("offerings.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_cleaned_data)

    print("✅ All pages scraped and saved to offerings.csv")
    input("\nPress Enter to close browser...")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
