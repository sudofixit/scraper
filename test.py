import os
import asyncio
import csv
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

# Initialize credentials
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
    await page.wait_for_selector("table")
    print("✅ Table found. Querying rows...")
    table = await page.query_selector("table")
    rows = await table.query_selector_all("tr")

    raw_data = []
    for i, row in enumerate(rows):
        cells = await row.query_selector_all("td")
        row_data = [await cell.inner_text() for cell in cells if cell]
        print(f"📦 Row {i}: {row_data}")
        if row_data:
            raw_data.append(row_data)

    header = [
        "Course", "Course Name", "Credits", "Instructor", "Room",
        "Days", "Start Time", "End Time", "Max Enrollment", "Total Enrollment"
    ]

    cleaned_data = []
    current_course = {}

    for row in raw_data:
        # Course metadata row (typically first row of a course group)
        if len(row) >= 7 and any(char.isdigit() for char in row[2]):
            current_course = {
                "code": row[0],
                "name": row[1],
                "credits": row[2],
                "max": row[-2],  # Second last element
                "total": row[-1]  # Last element
            }
        # Class session rows
        elif len(row) >= 6 and current_course:
            cleaned_data.append([
                current_course["code"],
                current_course["name"],
                current_course["credits"],
                row[0].strip(),  # Instructor
                row[1].strip(),  # Room
                row[2].strip(),  # Days
                row[3].strip(),  # Start Time
                row[4].strip(),  # End Time
                current_course["max"],
                current_course["total"]
            ])

    with open("offerings.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(cleaned_data)

    print("✅ Offerings table cleaned and saved to offerings.csv")
    input("\nPress Enter to close browser...")
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())