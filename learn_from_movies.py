import pysrt
import spacy

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
            self.save_read_text()
        else: 
            print("Błąd")

    def save_read_text(self):
        with open(f"{self.file_name}.txt", "w", encoding='utf-8') as file:
            for sub in self.subs:
                for key, value in self.to_change.items():
                    sub.text = sub.text.replace(key, value)
                file.write(sub.text)
        self.analyze_text()

    def analyze_text(self):
        with open(f"{self.file_name}.txt", "r") as file:
            self.text = file.read()
            self.doc = self.nlp(self.text)
            self.sentences = list(self.doc.sents)

            for sentence in self.sentences:
                for token in sentence:
                    if token.pos_ == "NOUN":
                        self.nouns.append(token.lemma_)
                    elif token.pos_ == "VERB":
                        self.verbs.append(token.lemma_)
        
        self.nouns = list(set(self.nouns))
        self.verbs = list(set(self.verbs))
        print("Rzeczowniki w formie ogólnej")
        print(self.nouns)
        print("Czasowniki w formie bezokolicznika")
        print(self.verbs)
        input()



if __name__ == "__main__":
    get_file = input("Podaj nazwę pliku .srt: ")
    text = Text(get_file)

    