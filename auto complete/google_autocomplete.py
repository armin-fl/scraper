import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import csv

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

def save_to_csv(file_path, data):
    """Save suggestions to a CSV file with UTF-8 encoding."""
    try:
        with open(file_path, "w", newline='', encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Suggestions"])  # Header
            for suggestion in data:
                writer.writerow([suggestion])
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
    results_list.delete(0, tk.END)  # Clear previous results
    for suggestion in suggestions:
        results_list.insert(tk.END, suggestion)

def on_save():
    """Handle the save button click."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save as"
    )
    if file_path:
        data = results_list.get(0, tk.END)  # Get all results from the listbox
        save_to_csv(file_path, data)

# GUI Setup
root = tk.Tk()
root.title("Google Autocomplete Suggestions")

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
fetch_button = tk.Button(root, text="Fetch Suggestions", command=on_fetch)
fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

# Results listbox
results_label = tk.Label(root, text="Suggestions:")
results_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
results_list = tk.Listbox(root, width=50, height=15)
results_list.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Save button
save_button = tk.Button(root, text="Save to CSV", command=on_save)
save_button.grid(row=6, column=0, columnspan=2, pady=10)

# Start the application
root.mainloop()
