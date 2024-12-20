import tkinter as tk
from tkinter import filedialog, ttk
import requests
import time
import csv
from bs4 import BeautifulSoup

# Persian expansion prefixes and alphabet variations
PERSIAN_PREFIXES = ["چگونه", "بهترین", "راهنمای", "خرید", "مقاله در مورد"]
PERSIAN_ALPHABET = ["ا", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ"]

# Default language and region
DEFAULT_LANG = "fa"
DEFAULT_REGION = "ir"

# Function to get Google Autocomplete suggestions
def get_autocomplete_suggestions(query, lang="fa"):
    suggestions = []
    url = f"https://suggestqueries.google.com/complete/search?hl={lang}&output=toolbar&q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'xml')
        for suggestion in soup.find_all('suggestion'):
            suggestions.append(suggestion['data'])
    except Exception as e:
        print(f"Error fetching Autocomplete: {e}")
    return suggestions

# Function to get People Also Ask (PAA) questions
def get_paa_questions(query):
    questions = []
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for elem in soup.find_all("div", class_="related-question-pair"):
            question = elem.text.strip()
            if question:
                questions.append(question)
    except Exception as e:
        print(f"Error fetching PAA: {e}")
    return questions

# Expand keywords using Persian prefixes and alphabet
def expand_keywords(seed):
    expanded_keywords = []
    for prefix in PERSIAN_PREFIXES:
        expanded_keywords.append(f"{prefix} {seed}")
    for letter in PERSIAN_ALPHABET:
        expanded_keywords.append(f"{seed} {letter}")
    return expanded_keywords

# Main function to handle scraping and saving
def main_scraper(seed_keywords, output_file, lang):
    all_results = []
    
    for seed in seed_keywords:
        print(f"Processing: {seed}")
        
        # Autocomplete suggestions
        autocomplete_results = set(get_autocomplete_suggestions(seed, lang))
        print(f" - Found {len(autocomplete_results)} Autocomplete suggestions")
        
        # Expand and collect deeper Autocomplete suggestions
        for expanded in expand_keywords(seed):
            new_suggestions = get_autocomplete_suggestions(expanded, lang)
            autocomplete_results.update(new_suggestions)
            time.sleep(2)  # Avoid rate limiting
        
        # PAA results
        paa_results = set(get_paa_questions(seed))
        print(f" - Found {len(paa_results)} PAA questions")
        
        # Combine results
        for suggestion in autocomplete_results:
            all_results.append([seed, suggestion, ""])
        for question in paa_results:
            all_results.append([seed, "", question])

        time.sleep(3)  # Rate limit between seeds
    
    # Save to CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Seed Keyword", "Autocomplete Suggestion", "PAA Question"])
        writer.writerows(all_results)
    print(f"Results saved to {output_file}")

# GUI for input
def start_gui():
    def run_script():
        seed_input = entry_keywords.get("1.0", tk.END).strip().split("\n")
        output_path = filedialog.asksaveasfilename(defaultextension=".csv")
        selected_lang = language_var.get()
        main_scraper(seed_input, output_path, selected_lang)
        result_label.config(text="Scraping Complete! File saved.")
    
    # GUI Window
    root = tk.Tk()
    root.title("Persian Keyword Scraper")
    root.geometry("500x500")
    
    # Input Section
    tk.Label(root, text="Enter Seed Keywords (one per line):").pack()
    entry_keywords = tk.Text(root, height=10)
    entry_keywords.pack()
    
    # Language Selection
    tk.Label(root, text="Select Language:").pack()
    language_var = tk.StringVar(value=DEFAULT_LANG)
    language_menu = ttk.Combobox(root, textvariable=language_var)
    language_menu['values'] = ["fa", "en", "ar", "tr", "de"]
    language_menu.pack()
    
    # Run Button
    tk.Button(root, text="Start Scraping", command=run_script).pack()
    
    # Result Label
    result_label = tk.Label(root, text="")
    result_label.pack()
    
    root.mainloop()

# Start GUI
if __name__ == "__main__":
    start_gui()
