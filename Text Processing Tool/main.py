import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tkinter.simpledialog import askinteger
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import time

def process_text_chunk(chunk, idx):
    words = chunk.split()
    word_count = Counter(words)
    return word_count

def split_text(text, num_chunks=4):
    chunk_size = len(text) // num_chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def process_with_index(chunk, idx):
    return process_text_chunk(chunk, idx)

def count_words_sequential(text, num_chunks=4):
    chunks = split_text(text, num_chunks)
    word_counts = Counter()
    
    for idx, chunk in enumerate(chunks, start=1):
        word_count = process_text_chunk(chunk, idx)
        word_counts.update(word_count)
    
    return word_counts

def count_words_parallel(text, num_chunks=4):
    chunks = split_text(text, num_chunks)
    word_counts = Counter()

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_with_index, chunks, range(1, len(chunks) + 1)))
    
    for result in results:
        word_counts.update(result)
    
    return word_counts

def process_text():
    input_text = text_input.get("1.0", tk.END).strip()
    
    if not input_text:
        messagebox.showerror("Error", "Please enter some text to process.")
        return

    mode = processing_mode.get()

    if mode == 'parallel':
        num_chunks = askinteger("Input", "Enter the number of chunks for parallel processing:", minvalue=1, maxvalue=100)
        if num_chunks is None:
            return
    else:
        num_chunks = 1

    process_button.config(state=tk.DISABLED)
    start_time = time.time()

    if mode == 'sequential':
        word_counts = count_words_sequential(input_text, num_chunks)
    elif mode == 'parallel':
        word_counts = count_words_parallel(input_text, num_chunks)
    else:
        messagebox.showerror("Error", "Please choose a valid processing mode.")
        return

    end_time = time.time()

    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "Word count summary:\n")
    for word, count in word_counts.items():
        result_text.insert(tk.END, f"'{word}': {count}\n")
    
    result_text.insert(tk.END, f"\nTime taken: {end_time - start_time:.2f} seconds")
    save_button.config(state=tk.NORMAL)
    process_button.config(state=tk.NORMAL)

def upload_file():
    file_path = filedialog.askopenfilename(title="Open a text file", filetypes=[("Text Files", "*.txt")])
    
    if file_path:
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
                text_input.delete("1.0", tk.END)
                text_input.insert(tk.END, file_content)
                text_input.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the file: {e}")

def save_file():
    result = result_text.get("1.0", tk.END).strip()
    
    if not result:
        messagebox.showwarning("Warning", "No results to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])

    if file_path:
        try:
            with open(file_path, 'w') as file:
                file.write(result)
            messagebox.showinfo("Success", f"Results saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

if __name__ == "__main__":
    window = tk.Tk()
    window.title("Text Processing Tool")

    upload_button = tk.Button(window, text="Upload Text File", command=upload_file)
    upload_button.pack(pady=10)

    text_input_label = tk.Label(window, text="Enter the text to process:")
    text_input_label.pack(pady=5)

    text_input = scrolledtext.ScrolledText(window, width=60, height=10)
    text_input.pack(pady=5)

    processing_mode = tk.StringVar(value='sequential')

    mode_frame = tk.Frame(window)
    mode_frame.pack(pady=10)

    sequential_radio = tk.Radiobutton(mode_frame, text="Sequential", variable=processing_mode, value='sequential')
    sequential_radio.grid(row=0, column=0, padx=10)

    parallel_radio = tk.Radiobutton(mode_frame, text="Parallel", variable=processing_mode, value='parallel')
    parallel_radio.grid(row=0, column=1, padx=10)

    process_button = tk.Button(window, text="Process Text", command=process_text)
    process_button.pack(pady=15)

    result_text_label = tk.Label(window, text="Processed Word Counts:")
    result_text_label.pack(pady=5)

    result_text = scrolledtext.ScrolledText(window, width=60, height=10)
    result_text.pack(pady=5)

    save_button = tk.Button(window, text="Save Results", command=save_file, state=tk.DISABLED)
    save_button.pack(pady=10)

    window.mainloop()