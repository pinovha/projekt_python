import pysrt
import spacy
import sqlite3

class Text:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split(".")[0]
        self.file_extension = file_path.split(".")[-1]
        self.to_change = {"\n\n": " ", "\n": " ", "\\": " ", "<i>": " ", "</i>": " ", ".": ". ", "?": "? ", "-": ""}
        self.nlp = spacy.load("en_core_web_sm")
        self.nouns = []
        self.verbs = []
        if self.file_extension == "srt": 
            self.subs = pysrt.open(file_path, encoding='iso-8859-1')
            self.process_text()
        else: 
            print("Program obsługuje jedynie pliki .srt")


    def process_text(self):
        self.text = ""
        for sub in self.subs:
            for key, value in self.to_change.items():
                sub.text = sub.text.replace(key, value)
            self.text += sub.text
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

        for item in self.items:
            print(item)


if __name__ == "__main__":
    #text = Text("Prison Break S01E01.srt")
    db = DataBase()
    #db.get_table("nouns")
    #db.get_table("verbs")