import pysrt
import spacy
import sqlite3
import tkinter as tk
import io

class Text:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split(".")[0]
        self.file_extension = file_path.split(".")[-1]
        self.to_change = {"\n\n": " ", "\n": " ", "\\": " ", "<i>": " ", "</i>": " ", ".": " ", "?": " ", "-": " ", "%": " "}
        self.nlp = spacy.load("en_core_web_sm")
        self.nouns1 = []
        self.verbs = []
        if self.file_extension == "srt": 
            self.subs = pysrt.open(file_path, encoding='iso-8859-1')
            self.process_text()
        elif self.file_extension == "txt": 
            self.subs = open(file_path)
            self.process_text()
            print("Program obsługuje jedynie pliki .srt")
        else:
            print("Podałeś plik o rozszerzeniu innym niż srt lub txt.")


    def process_text(self):
        self.text = ""
        if isinstance(self.subs, pysrt.SubRipFile):
            for sub in self.subs:
                for key, value in self.to_change.items():
                    sub.text = sub.text.replace(key, value)
                self.text += sub.text
        elif isinstance(self.subs, io.TextIOWrapper):
            for line in self.subs:
                for key, value in self.to_change.items():
                    line = line.replace(key, value)
                self.text += line
        else:
            print("Nieobsługiwany typ obiektu self.subs")

        self.analyze_text()


    def analyze_text(self):
        self.doc = self.nlp(self.text)
        self.sentences = list(self.doc.sents)
        db = DataBase()

        for sentence in self.sentences:
            for token in sentence:
                if token.pos_ == "NOUN":
                    db.add_word("nouns", token.lemma_, 0, self.file_name)
                elif token.pos_ == "VERB":
                    db.add_word("verbs", token.lemma_, 0, self.file_name)


class DataBase:
    def __init__(self, db_name='database.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_db()


    def create_db(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS nouns(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word TEXT,
                        known INTEGER,
                        name TEXT)""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS verbs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word TEXT,
                        known INTEGER,
                        name TEXT)""")
        self.conn.commit()


    def word_exists(self, table, word, name):
        self.c.execute(f"SELECT COUNT(*) FROM {table} WHERE word=? AND name=?", (word, name))
        result = self.c.fetchone()
        return result[0] > 0


    def add_word(self, table, word, known, name):
        if not self.word_exists(table, word, name):
            self.c.execute(f"INSERT INTO {table} (word, known, name) VALUES (?, ?, ?)", (word, known, name))
            self.conn.commit()
            print("Dodano słowo do bazy danych.")
        else:
            print("Słowo już istnieje w bazie danych.")


    def get_table(self, table):
        self.c.execute(f"SELECT word FROM {table}")
        self.items = self.c.fetchall()
        return self.items


class Tkinter_GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("400x500")
        self.root.title("Learn From Movies")

        frame_menu = tk.Frame(self.root, bg='gray')
        frame_menu.pack(fill="x")
        frame_menu.configure( height=100)
        frame_menu.pack_propagate(False)

        label = tk.Label(frame_menu, text="Ucz Się Języka Ze Skryptów", font=('Arial', 17))
        label.pack(pady=20)

        button_frame = tk.Frame(self.root)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.pack(fill="x")
        button1 = tk.Button(button_frame, text="Słowa do nauki", font=("Arial", 9), command=lambda: self.home_page())
        button1.grid(row=0, column=0, sticky="we")
        button2 = tk.Button(button_frame, text="Poznane słowa", font=("Arial", 9), comman=lambda: self.second_page())
        button2.grid(row=0, column=1, sticky="we")

        self.frame_main = tk.Frame(self.root, bg='yellow')
        self.frame_main.pack(fill="both", expand=True)
        self.frame_main.pack_propagate(False)

        self.current_frame = None


    def home_page(self):
        self.is_not_none(self.current_frame) # Sprawdza czy dany Frame istnieje, jeśli tak to go usuwa.
        self.current_frame = tk.Frame(self.frame_main, bg="white")
        self.current_frame.pack_propagate(False)
        self.current_frame.pack(fill="both", expand=True)

        db = DataBase()
        self.nouns = db.get_table("nouns")

        self.items_per_page = 10
        self.current_page = 0

        self.lb_frame = tk.Frame(self.current_frame)
        self.lb_frame.columnconfigure(0, weight=1)
        self.lb_frame.columnconfigure(1, weight=1)
        self.lb_frame.pack(fill="x")

        self.display_page(self.current_page)

        button_frame2 = tk.Frame(self.current_frame)
        button_frame2.columnconfigure(0, weight=1)
        button_frame2.columnconfigure(1, weight=1)
        button_frame2.pack(fill="x", side="bottom")

        previous_button = tk.Button(button_frame2, text="Poprzednia strona", height=2, font=("Arial", 9), command=self.previous_page)
        previous_button.grid(row=0, column=0, sticky="we")

        next_button = tk.Button(button_frame2, text="Następna strona", height=2, font=("Arial", 9), command=self.next_page)
        next_button.grid(row=0, column=1, sticky="we")




    def display_page(self, page):
        self.current_page = page
        start_index = page * self.items_per_page
        end_index = start_index + self.items_per_page

        # Usuwa poprzednie Label'y, aby wyświetlić nowe.
        for widget in self.current_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()

        # Usuwa elementy w lb_frame, aby wyświetlić nowe.
        for widget in self.lb_frame.winfo_children():
            widget.destroy()
            
        for i, row in enumerate(self.nouns[start_index:end_index]):
            lb1 = tk.Label(self.lb_frame, text=row, font=("Arial", 17), justify="center")
            lb1.grid(row=i, column=0, sticky="we")
            
            lb2 = tk.Label(self.lb_frame, text=row, font=("Arial", 17), justify="center")
            lb2.grid(row=i, column=1, sticky="we")


    def next_page(self):
        total_pages = len(self.nouns) // self.items_per_page
        if self.current_page < total_pages:
            self.display_page(self.current_page + 1)


    def previous_page(self):
        if self.current_page > 0:
            self.display_page(self.current_page - 1)


    def second_page(self):
        self.is_not_none(self.current_frame)
        self.current_frame = tk.Frame(self.frame_main, bg="white")
        self.current_frame.pack_propagate(False)
        self.current_frame.pack(fill="both", expand=True)


# Używane do usuwania Frame, przed wyświetleniem nowego.
    def is_not_none(self, obj):
        if obj is not None:
            obj.destroy()


if __name__ == "__main__":
    # -- INPUT file
    #text = Text("plik.txt")
    # -- Run GUI
    app = Tkinter_GUI()
    app.root.mainloop()