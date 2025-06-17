import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import ollama
import html
import time

def get_simplified_translation(text_to_translate):
    """
    Sends the text to the Ollama model and returns the simplified translation.
    """
    print(f"Sending to Ollama: {text_to_translate}")
    try:
        prompt = """Below is an instruction on how to translate text from complex and archaic to simple and modern english.The input contains this text. Write in the response a faithful translation.### Instruction:Translate the following line from complex to simple english.It may contain archaic and literary words or structures: make them easily understandable.### Input:{}### Response:{}"""
        t1 = time.time()
        final_prompt = prompt.format(text_to_translate, "")
        response = ollama.generate(
            model='gem',
            prompt=final_prompt,
            stream=False
        )
        t2 = time.time()
        prompt_new = """Translate the text I will give you in PIECE to modern and simpler english, easily understandable also for non-native speakers,
        keeping the meaning intact. If the text is already modern and simple, return it as is. Do not add any introduction, extra text or
        explanation, just answer with the translation.

        ### PIECE:
        {}

        ### TRANSLATION:
        {}"""
        final_prompt_new = prompt_new.format(text_to_translate, "")
        response_new = ollama.generate(
            model='gemma-3-finetune-v3',
            prompt=final_prompt_new,
            stream=False
        )
        t3 = time.time()

        if 'response' in response and response['response']:
            translation = response['response']
            translation_new = response_new['response']
            print(f"Ollama responses: {translation}\nNew: {translation_new}")
            print(f"Time taken for first Ollama call: {t2 - t1:.3f} seconds")
            print(f"Time taken for new Ollama call: {t3 - t2:.3f} seconds")
            return translation + '\n\n' + translation_new
        else:
            print("Ollama returned an empty or invalid response.")
            return "[Translation Error: Empty response from model]"

    except Exception as e:
        print(f"Error calling Ollama: {e}")
        if "model not found" in str(e):
             return f"[Translation Error: Model 'gem' not found. Ensure Ollama is running and the model is available.]"
        return f"[Translation Error: {e}]"


class EbookReaderApp:
    def __init__(self, root):
        """
        Initializes the Ebook Reader application UI.
        """
        self.root = root
        self.root.title("Simple Ebook Reader")
        self.root.geometry("800x600")

        self.book = None
        self.chapters = []
        self.chapter_titles = []
        self.current_chapter_index = 0
        self.fonts = ("Arial", 12)

        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open EPUB", command=self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        root.config(menu=self.menu_bar)

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.text_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            font=self.fonts,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        self.control_frame = tk.Frame(self.main_frame, pady=5)
        self.control_frame.pack(fill=tk.X)

        self.prev_button = tk.Button(self.control_frame, text="<< Previous", command=self.prev_chapter, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.chapter_label = tk.Label(self.control_frame, text="Chapter: -/-")
        self.chapter_label.pack(side=tk.LEFT, expand=True)

        self.next_button = tk.Button(self.control_frame, text="Next >>", command=self.next_chapter, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=5)

        self.translate_button = tk.Button(self.main_frame, text="Translate Selection", command=self.translate_selection, state=tk.DISABLED)
        self.translate_button.pack(pady=5)


    def open_file(self):
        """
        Opens a file dialog to select an EPUB file and loads it.
        """
        filepath = filedialog.askopenfilename(
            title="Open EPUB File",
            filetypes=[("EPUB files", "*.epub")]
        )
        if not filepath:
            return

        try:
            self.load_epub(filepath)
        except Exception as e:
            messagebox.showerror("Error Loading EPUB", f"Failed to load the EPUB file.\nError: {e}")
            self.reset_reader_state()


    def load_epub(self, filepath):
        """
        Loads and parses the EPUB file using EbookLib.
        Extracts chapters and prepares them for display.
        (Revised to handle TOC errors)
        """
        print(f"Loading EPUB: {filepath}")
        self.reset_reader_state()
        self.book = epub.read_epub(filepath, options={'ignore_ncx': True})
        self.chapters = []
        self.chapter_titles = []

        for item_id in self.book.spine:
            item = self.book.get_item_with_id(item_id[0])
            if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                html_content = item.get_content().decode('utf-8', errors='ignore')
                self.chapters.append(html_content)
                title = item.get_name()
                self.chapter_titles.append(title if title else f"Chapter {len(self.chapters)}")


        if not self.chapters:
             print("Spine empty or yielded no content, trying all HTML items...")
             html_items = self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
             for item in html_items:
                 html_content = item.get_content().decode('utf-8', errors='ignore')
                 self.chapters.append(html_content)
                 title = item.get_name()
                 self.chapter_titles.append(title if title else f"Chapter {len(self.chapters)}")


        if self.chapters:
            print(f"Loaded {len(self.chapters)} chapters.")
            self.current_chapter_index = 0
            self.display_chapter()
            self.update_navigation_buttons()
            self.translate_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Empty Book", "Could not find any readable content in the EPUB.")
            self.reset_reader_state()

    def display_chapter(self):
        """
        Displays the content of the current chapter in the text area.
        Uses BeautifulSoup to extract text from HTML.
        """
        if not self.chapters or not (0 <= self.current_chapter_index < len(self.chapters)):
            return

        html_content = self.chapters[self.current_chapter_index]
        soup = BeautifulSoup(html_content, 'html.parser')

        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])
        if paragraphs:
             chapter_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
             chapter_text = soup.get_text(separator="\n", strip=True)

        chapter_text = html.unescape(chapter_text)

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, chapter_text)
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview_moveto(0.0)

        title = self.chapter_titles[self.current_chapter_index] if self.chapter_titles else f"Chapter {self.current_chapter_index + 1}"
        self.chapter_label.config(text=f"{title} ({self.current_chapter_index + 1}/{len(self.chapters)})")


    def update_navigation_buttons(self):
        """
        Enables or disables the Previous/Next buttons based on the current chapter index.
        """
        if not self.chapters:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            return

        if self.current_chapter_index > 0:
            self.prev_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)

        if self.current_chapter_index < len(self.chapters) - 1:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)


    def next_chapter(self):
        """
        Moves to the next chapter and updates the display.
        """
        if self.chapters and self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            self.display_chapter()
            self.update_navigation_buttons()


    def prev_chapter(self):
        """
        Moves to the previous chapter and updates the display.
        """
        if self.chapters and self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.display_chapter()
            self.update_navigation_buttons()


    def translate_selection(self):
        """
        Gets the selected text from the text area, calls the translation function,
        and displays the result in a popup window.
        """
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please select some text to translate.")
            return

        if not selected_text:
            messagebox.showinfo("No Selection", "Please select some text to translate.")
            return

        translation = get_simplified_translation(selected_text)

        self.show_translation_popup(selected_text, translation)


    def show_translation_popup(self, original, translation):
        """
        Creates and displays a new top-level window showing the original
        text and its translation.
        """
        popup = tk.Toplevel(self.root)
        popup.title("Simplified Translation")
        popup.geometry("500x300")

        popup_frame = tk.Frame(popup, padx=10, pady=10)
        popup_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(popup_frame, text="Original Text:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        original_text_widget = scrolledtext.ScrolledText(popup_frame, wrap=tk.WORD, height=5, font=self.fonts)
        original_text_widget.pack(fill=tk.X, pady=(0, 10))
        original_text_widget.insert(tk.END, original)
        original_text_widget.config(state=tk.DISABLED)

        tk.Label(popup_frame, text="Simplified Text:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        translation_text_widget = scrolledtext.ScrolledText(popup_frame, wrap=tk.WORD, height=8, font=self.fonts)
        translation_text_widget.pack(fill=tk.BOTH, expand=True)
        translation_text_widget.insert(tk.END, translation)
        translation_text_widget.config(state=tk.DISABLED)

        close_button = tk.Button(popup_frame, text="Close", command=popup.destroy)
        close_button.pack(pady=(10, 0))

        popup.transient(self.root)
        popup.grab_set()
        self.root.wait_window(popup)


    def reset_reader_state(self):
        """
        Resets the application state when a new file is opened or loading fails.
        """
        self.book = None
        self.chapters = []
        self.chapter_titles = []
        self.current_chapter_index = 0
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.chapter_label.config(text="Chapter: -/-")
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.translate_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = EbookReaderApp(root)
    root.mainloop()