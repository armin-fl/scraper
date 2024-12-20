import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Persian alphabet for keyword expansion
PERSIAN_ALPHABET = 'ا ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ه ی'.split()

def fetch_suggestions(query, language, region):
    """Fetch suggestions from Google Autocomplete API."""
    url = "http://suggestqueries.google.com/complete/search"
    params = {
        "q": query,
        "hl": language,  # Language code
        "gl": region,    # Region code
        "client": "firefox"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            return data[1]  # Suggestions are in the second index of the response
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse API response: {e}")
            return []
    else:
        messagebox.showerror("Error", f"Failed to fetch suggestions: {response.status_code}")
        return []

def expand_query_and_fetch(query, language, region):
    """Expand the query using the Persian alphabet and fetch suggestions."""
    suggestions = set()
    for letter in PERSIAN_ALPHABET:
        expanded_query = f"{query} {letter}"
        suggestions.update(fetch_suggestions(expanded_query, language, region))
        if len(suggestions) >= 100:  # Stop if we reach 100 suggestions
            break
    return list(suggestions)[:100]

def fetch_paa_questions(query):
    """Fetch People Also Ask questions using Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    paa_questions = set()
    try:
        # Navigate to Google search
        driver.get("https://www.google.com/")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)  # Allow page to load
        
        # Expand PAA questions and extract them
        while len(paa_questions) < 100:
            try:
                questions = driver.find_elements(By.XPATH, "//div[@class='related-question-pair']//span")
                for question in questions:
                    paa_questions.add(question.text)
                # Click on a question to load more PAA
                expandable_questions = driver.find_elements(By.XPATH, "//div[@class='related-question-pair']")
                if expandable_questions:
                    expandable_questions[0].click()
                    time.sleep(1)  # Allow new questions to load
                else:
                    break
            except Exception as e:
                break
    finally:
        driver.quit()
    return list(paa_questions)[:100]

def save_to_csv(file_path, google_suggestions, paa_questions):
    """Save Google suggestions and PAA questions to separate sections in a CSV file."""
    try:
        with open(file_path, "w", newline='', encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Google Suggestions"])  # Header
            for suggestion in google_suggestions:
                writer.writerow([suggestion])
            writer.writerow([])  # Empty row as separator
            writer.writerow(["People Also Ask"])  # Header
            for question in paa_questions:
                writer.writerow([question])
        messagebox.showinfo("Success", f"Suggestions saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

def on_fetch():
    """Handle the fetch button click."""
    query = query_entry.get()
    language = language_var.get()
    region = region_var.get()
    
    if not query:
        messagebox.showerror("Error", "Query cannot be empty.")
        return

    # Fetch and expand suggestions
    suggestions = expand_query_and_fetch(query, language, region)
    google_suggestions_list.delete(0, tk.END)  # Clear previous results
    for suggestion in suggestions:
        google_suggestions_list.insert(tk.END, suggestion)

    # Fetch PAA questions
    paa_questions = fetch_paa_questions(query)
    paa_list.delete(0, tk.END)  # Clear previous results
    for question in paa_questions:
        paa_list.insert(tk.END, question)

def on_save():
    """Handle the save button click."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save as"
    )
    if file_path:
        google_suggestions = google_suggestions_list.get(0, tk.END)  # Get all Google suggestions
        paa_questions = paa_list.get(0, tk.END)  # Get all PAA questions
        save_to_csv(file_path, google_suggestions, paa_questions)

# GUI Setup
root = tk.Tk()
root.title("Keyword Research Tool")

# Query input
query_label = tk.Label(root, text="Query:")
query_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
query_entry = tk.Entry(root, width=40)
query_entry.grid(row=0, column=1, padx=5, pady=5)

# Language selection
language_label = tk.Label(root, text="Language:")
language_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
language_var = tk.StringVar(value="fa")  # Default to Persian
language_entry = ttk.Entry(root, textvariable=language_var, width=10)
language_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

# Region selection
region_label = tk.Label(root, text="Region:")
region_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
region_var = tk.StringVar(value="IR")  # Default to Iran
region_entry = ttk.Entry(root, textvariable=region_var, width=10)
region_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

# Fetch button
fetch_button = tk.Button(root, text="Fetch Data", command=on_fetch)
fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

# Google Suggestions listbox
google_suggestions_label = tk.Label(root, text="Google Suggestions:")
google_suggestions_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
google_suggestions_list = tk.Listbox(root, width=50, height=10)
google_suggestions_list.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# PAA listbox
paa_label = tk.Label(root, text="People Also Ask:")
paa_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
paa_list = tk.Listbox(root, width=50, height=10)
paa_list.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Save button
save_button = tk.Button(root, text="Save to CSV", command=on_save)
save_button.grid(row=8, column=0, columnspan=2, pady=10)

# Start the application
root.mainloop()
