import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# Setup Selenium WebDriver with a regional setting
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (without GUI)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to fetch "People Also Ask" questions for a keyword
def fetch_paa_questions(keyword, max_questions=100):
    driver = setup_driver()
    query = keyword + " site:google.com"
    url = f"https://www.google.com/search?q={query}&hl=fa&gl=IR"  # Persian language and Iran region
    driver.get(url)

    # Allow time for the page to load
    time.sleep(3)

    questions = []
    try:
        # Find the People Also Ask questions (the divs containing questions)
        paa_elements = driver.find_elements(By.CSS_SELECTOR, '.n0jXd')
        for element in paa_elements:
            question = element.text
            questions.append(question)
            if len(questions) >= max_questions:
                break

        # Handle opening more questions by interacting with the page (if needed)
        # For example, clicking on a question to load more PAA questions
        while len(questions) < max_questions:
            try:
                next_question = driver.find_element(By.CSS_SELECTOR, '.n0jXd')
                actions = ActionChains(driver)
                actions.move_to_element(next_question).click().perform()
                time.sleep(2)
                new_paa_elements = driver.find_elements(By.CSS_SELECTOR, '.n0jXd')
                for new_element in new_paa_elements:
                    question = new_element.text
                    if question not in questions:
                        questions.append(question)
                    if len(questions) >= max_questions:
                        break
            except Exception as e:
                print(f"Error interacting with page: {e}")
                break

    except Exception as e:
        print("Error fetching PAA questions:", e)

    driver.quit()
    return questions

# Save the questions to a CSV file
def save_to_csv(questions, filename="paa_questions.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Question"])
        for question in questions:
            writer.writerow([question])

if __name__ == "__main__":
    keyword = "بهترین راه یادگیری پایتون"  # Example Persian keyword
    max_questions = 100
    questions = fetch_paa_questions(keyword, max_questions)
    save_to_csv(questions, "paa_questions.csv")
    print(f"Saved {len(questions)} questions to paa_questions.csv")
