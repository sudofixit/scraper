import os
import sys
import asyncio
import csv
from dotenv import dotenv_values
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig

def get_credentials():
    creds = dotenv_values(".env")
    return creds.get("ID"), creds.get("PASSWORD"), creds.get("GEMINI_API_KEY"), creds.get("TERM")

async def extract_page_data(page):
    try:
        await page.wait_for_selector("table", timeout=8000)
        table = await page.query_selector("table")
        if not table:
            print("⚠️ No table found on page")
            return []
            
        rows = await table.query_selector_all("tr")
        raw_data = []
        for row in rows:
            cells = await row.query_selector_all("td")
            row_data = [await cell.inner_text() for cell in cells if cell]
            if row_data:
                raw_data.append(row_data)
        return raw_data
    except Exception as e:
        print(f"❌ Table extraction error: {e}")
        return []

async def click_next_page(page, current):
    try:
        next_button = await page.query_selector(f"text='{current + 1}'")
        if next_button:
            await next_button.click()
            await page.wait_for_timeout(2000)  # Increased wait time
            return True
        print(f"⚠️ Next button for page {current + 1} not found")
        return False
    except Exception as e:
        print(f"❌ Page navigation error: {e}")
        return False

async def main():
    ID, PASSWORD, GEMINI_API_KEY, TERM = get_credentials()
    
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

    context = await browser.new_context()

    task = (
        "1. Go to https://cudportal.cud.ac.ae/student/login.asp\n"
        "2. Wait for login page to load\n"
        "3. Click on #username input field\n"
        f"4. Type '{ID}' into #username\n"
        "5. Click on #password input field\n"
        f"6. Type '{PASSWORD}' into #password\n"
        "7. Find the term dropdown under the password field\n"
        f"8. Select the dropdown option with value '{TERM}'\n"
        "9. Click on input[type='submit']\n"
        "10. Wait for navigation to complete\n"
        "11. Navigate to Offerings section\n"
        "12. Apply SEAST filter\n"
        "13. Wait 3 seconds for page refresh\n"
        "14. Verify filter application"
    )

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        browser_context=context
    )

    await agent.run()
    page = await context.get_current_page()

    try:
        await page.wait_for_selector("text='Course Offering'", timeout=15000)
        print("✅ Navigation verification passed")
    except Exception as e:
        print(f"❌ Page verification failed: {e}")
        await browser.close()
        return "invalid"

    print("✅ Login & navigation successful! Starting to scrape...")

    header = [
        "Course", "Course Name", "Credits", "Instructor", "Room",
        "Days", "Date", "Start Time", "End Time", "Max Enrollment", "Total Enrollment"
    ]

    all_cleaned_data = []
    current_page = 1
    total_pages = 8
    last_course_key = None

    try:
        while current_page <= total_pages:
            print(f"📄 Scraping Page {current_page}/{total_pages}")
            raw_data = await extract_page_data(page)
            
            if not raw_data:
                print("⚠️ No data found on page")
                break

            current_course = None
            for row in raw_data:
                if len(row) == 7 and "Credits" not in row[2]:
                    course_key = f"{row[0]}|{row[1]}"
                    if course_key == last_course_key:
                        continue
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
                    print("⏹️ Stopping pagination")
                    break
            current_page += 1

        with open("offerings.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(all_cleaned_data)

        print("✅ Scraping complete. Data saved to offerings.csv.")
        await browser.close()
        return "success"

    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        await browser.close()
        return "error"

if __name__ == "__main__":
    asyncio.run(main())
