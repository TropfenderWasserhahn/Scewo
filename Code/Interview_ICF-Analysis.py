# This script will open the interview transcript, analyse it, assign ICF-Codes to the answers and store them in a separate file.
# The ICF-Codes will be ordinalised. Answers that are negative will be result in -1 , no comment in 0 and positive answers in 1.
# The files can then be used for further analysis, e.g. a Heatmap, comparing the mentioned ICF-Codes to the used wheelchair.
# It uses different packages to recognize similar words and word stems.

import pandas as pd # pip install pandas
import re
import docx     # pip install python-docx
import spacy    # pip install spacy
import os
import nltk    # pip install nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

# Load NLP-models
nlp = spacy.load("de_core_web_sm")
nltk.download('vader_lexicon')
nltk.download('punkt')

# Initialise sentiment-analysis
sia = SentimentIntensityAnalyzer()

# Define path and function to load data
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../Data")
os.makedirs(data_dir, exist_ok=True)
output_dir = os.path.join(base_dir, "../Output")
os.makedirs(output_dir, exist_ok=True)

# Mapping of ICF-Codes to keywords 
icf_mapping = {
    "steuern|bedienen|modi wechseln": "d570",
    "mobilität|fortbewegung|gehen|fahren": "d460",
    "problem|schwierig|anstrengend|ermüdend": "b755",
    "treppen|steigung|hochfahren|hindernis": "d410",
    "enge räume|barriere|schwer zu wenden": "e150",
    "sicher|stabil|vertrauen": "b1266",
}

# Read the interview transcript
def read_docx(file_path):
    doc = docx.Document(file_path)  # Open the docx-file
    text = "\n".join([p.text for p in doc.paragraphs])  # Extract the text
    return text # Return the text as string

# Function for NLP-processing and sentiment-analysis
def process_text(text):
    doc = nlp(text.lower())  # Tokenizing and lowercasing
    tokens = [token.lemma_ for token in doc if not token.is_stop]  # Lemmatize and remove stopwords
    sentiment_score = sia.polarity_scores(text)["compound"]  # Sentiment-analysis(score between -1 and 1)

    return " ".join(tokens), sentiment_score    # Return the processed text and sentiment-score

# Funktion zur ICF-Kodierung basierend auf NLP-Analyse
def encode_icf(answers):
    icf_codes = {code: 0 for code in icf_mapping.values()}  # Alle Codes auf 0 setzen
    
    for answer in answers:
        processed_answer, sentiment = process_text(answer)  # NLP & Sentiment-Analyse
        for keyword, icf_code in icf_mapping.items():
            if re.search(keyword, processed_answer, re.IGNORECASE):
                icf_codes[icf_code] = 1 if sentiment > 0 else -1  # Sentiment entscheidet, ob positiv oder negativ

    return icf_codes

# Funktion zum Extrahieren der Patient-ID und Dateinamen
def extract_patient_id_and_filename(file_path):
    filename = os.path.basename(file_path)  # Holt den Dateinamen (z. B. "P01_M1_Interview.docx")
    match = re.search(r"(P\d+_M\d+)_Interview", filename)  # Regex sucht nach "Pxx_Mx_Interview"
    return match.group(1) if match else "Unknown"

# Funktion zur Verarbeitung des Interviews
def process_interview(file_path):
    if not file_path.endswith(".docx"):
        print("❌ Fehler: Datei muss im .docx-Format sein!")
        return

    if not os.path.exists(file_path):
        print(f"❌ Fehler: Die Datei '{file_path}' wurde nicht gefunden.")
        return

    # Patient-ID und Dateiname extrahieren
    patient_id_filename = extract_patient_id_and_filename(file_path)
    print(f"📌 Verarbeite Datei für: {patient_id_filename}")

    # Datei einlesen
    text = read_docx(file_path)
    answers = text.split("\n")  # Trenne Antworten an Zeilenumbrüchen

    results = []
    
    for idx, answer in enumerate(answers):
        icf_data = encode_icf([answer])  # Antwort analysieren und ICF-Codes zuweisen
        row = {"Patient_ID": patient_id_filename, "Frage_ID": idx + 1, "Antwort": answer}
        row.update(icf_data)  # ICF-Codes als Spalten hinzufügen
        results.append(row)

    # Speichere die Datei mit der richtigen Namensstruktur als CSV
    output_filename = f"{patient_id_filename}_Interview.csv"
    output_path = os.path.join(output_dir, output_filename)
    df_result = pd.DataFrame(results)
    df_result.to_csv(output_path, index=False)

    print(f"✅ ICF-kodierte Daten gespeichert in: {output_path}")

# Terminal-Input für Dateiname**
if __name__ == "__main__":
    file_name = input("📂 Gib den Namen der Datei (ohne .docx) ein: ")
    file_path = os.path.join(base_dir, f"{file_name}.docx")
    process_interview(file_path)