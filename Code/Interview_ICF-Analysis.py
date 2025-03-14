import os
import re
import pandas as pd
import docx
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

# NLTK-Modelle herunterladen (einmalig nötig)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('vader_lexicon')

# Initialisierung der NLP-Tools
lemmatizer = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()

# Basisverzeichnis setzen
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../Data")  # Datenverzeichnis
output_dir = os.path.join(base_dir, "../Output")  # Ausgabeverzeichnis
os.makedirs(data_dir, exist_ok=True)  
os.makedirs(output_dir, exist_ok=True)  

# ICF-Mapping mit erweiterten Schlüsselwörtern
icf_mapping = {
    "steuern|bedienen|modi wechseln": "d570",
    "mobilität|fortbewegung|gehen|fahren": "d460",
    "problem|schwierig|anstrengend|ermüdend": "b755",
    "treppen|steigung|hochfahren|hindernis": "d410",
    "enge räume|barriere|schwer zu wenden": "e150",
    "sicher|stabil|vertrauen": "b1266",
    "küche|kurze wege|gewöhnungsbedürftig": "d230",
    "sitzlift|positiv|hilfsmittel": "e120",
    "wendigkeit|manövrieren|leicht": "d435",
    "handling|bedienung|angenehm": "d465",
    "rückfahrkamera|nicht ideal": "e1301",
    "federung|spastik|angenehm": "b780",
    "unebener boden|angenehm|komfortabel": "d4551",
    "einkaufen|bankgeschäfte|treffen": "d620",
    "cafe|treppen|angenehm": "d4601",
    "leistung|stärke|power": "b740"
}

# Funktion zum Einlesen eines Word-Dokuments
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

# Funktion zur NLP-Verarbeitung & Sentiment-Analyse mit NLTK
# Alternative Funktion zur Textverarbeitung (ohne word_tokenize)
def process_text(text):
    tokens = text.lower().split()  # Split statt word_tokenize
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w.isalpha()]  # Lemmatisierung & nur Wörter behalten
    sentiment_score = sia.polarity_scores(text)["compound"]  # Sentiment-Analyse (Wert zwischen -1 und 1)
    
    return " ".join(tokens), sentiment_score


# Funktion zur ICF-Kodierung basierend auf NLP-Analyse
def encode_icf(answers):
    icf_codes = {code: 0 for code in icf_mapping.values()}  
    
    for answer in answers:
        processed_answer, sentiment = process_text(answer)  
        for keyword, icf_code in icf_mapping.items():
            if re.search(keyword, processed_answer, re.IGNORECASE):
                icf_codes[icf_code] = 1 if sentiment > 0 else -1  

    return icf_codes

# Funktion zum Extrahieren der Patient-ID und Dateinamen
def extract_patient_id_and_filename(file_path):
    filename = os.path.basename(file_path)  
    match = re.search(r"(P\d+_M\d+)_Interview", filename)  
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
    answers = text.split("\n")  

    results = []
    
    for idx, answer in enumerate(answers):
        icf_data = encode_icf([answer])  
        row = {"Patient_ID": patient_id_filename, "Frage_ID": idx + 1, "Antwort": answer}
        row.update(icf_data)  
        results.append(row)

    # Erstelle DataFrame
    df_result = pd.DataFrame(results)

    # **Speicherung als CSV und Excel**
    output_filename_csv = f"{patient_id_filename}_Interview.csv"
    output_filename_xlsx = f"{patient_id_filename}_Interview.xlsx"
    
    output_path_csv = os.path.join(output_dir, output_filename_csv)
    output_path_xlsx = os.path.join(output_dir, output_filename_xlsx)
    
    df_result.to_csv(output_path_csv, index=False)  # Speichere als CSV
    df_result.to_excel(output_path_xlsx, index=False)  # Speichere als Excel
    
    print(f"✅ ICF-kodierte Daten gespeichert in: {output_path_csv}")
    print(f"✅ ICF-kodierte Daten gespeichert in: {output_path_xlsx}")

# **Terminal-Input für Dateiname**
if __name__ == "__main__":
    file_name = input("📂 Gib den Namen der Datei (ohne .docx) ein: ")
    file_path = os.path.join(data_dir, f"{file_name}.docx")
    process_interview(file_path)
