# Hier importieren wir die benötigten Softwarebibliotheken.
from os.path import abspath, exists
from sys import argv
from streamlit import (
    text_input, header, title, subheader, container,
    markdown, link_button, divider, set_page_config, segmented_control, toggle, spinner, image)
from pyterrier import IndexFactory
from pyterrier.terrier import Retriever
from pyterrier.text import get_text
from openai import OpenAI
from pyterrier_dr import SBertBiEncoder


def set_custom_font():
    font_css = '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Inter:wght@400;500&display=swap');

    body {
        font-family: 'Inter', sans-serif !important;
    }

    h1, h2, h3 {
        font-family: 'Oswald', sans-serif !important;
    }
    </style>
    '''
    markdown(font_css, unsafe_allow_html=True)

def get_ai_snippet_titel(text: str, query: str) -> str:
    prompt = (
        "Fasse den folgenden Text in höchstens 8 Wörten auf Deutsch , "
        f"mit Bezug auf die Suchanfrage '{query}' in einem Passenden Titel zusammen verwende dafür nicht zwangsläufig die Suchanfrage. "
        "Gib Preise dabei exakt wie im Originaltext wieder, wenn vorhanden:\n\n"
        f"{text}"
    )

    client = OpenAI(
        api_key="glpat-pYioAiJD2cny6FMAdCjWjm86MQp1OmR3bQk.01.0z0qrxhou",  # denk an st.secrets, siehe unten
        base_url="https://api.blablador.fz-juelich.de/v1/",
    )
    response = client.responses.create(
        model="alias-fast",
        input=prompt,
    )
    return response.output_text

def get_ai_snippet_summary(text: str, query: str) -> str:
    prompt = (
        "Fasse den folgenden Text in höchstens 30 Wörten auf Deutsch zusammen, "
        f"mit Bezug auf die Suchanfrage '{query}'. "
        "Gib Preise dabei exakt wie im Originaltext wieder:\n\n"
        f"{text}"
    )

    client = OpenAI(
        api_key="glpat-pYioAiJD2cny6FMAdCjWjm86MQp1OmR3bQk.01.0z0qrxhou",  # denk an st.secrets, siehe unten
        base_url="https://api.blablador.fz-juelich.de/v1/",
    )
    response = client.responses.create(
        model="alias-fast",
        input=prompt,
    )
    return response.output_text

#definiert den prompt für Blablador und führt ihn aus, damit nicht überall das selbe steht
def aisnippet(result)->str:
    snippet_lines = [
        "\n",
        "Titel: " + result["title"],
        "Text: " + result["text"].replace("\n", " "),
        "URL: " + result["url"],
    ]
    #snippetlines = snippet_lines.replace("\n", " ")
    return "\n".join(snippet_lines)


def allsnippet(results, query, selection) -> str:
    if selection == "News":
        # das ist der news prompt
        aisnippets = "Beantworte die Frage '" + query + "' in insgesamt höchstens 50 Wörten auf deutsch mithilfe der Suchergebnisse :\n\n"
        for _, result in results.iterrows():
            aisnippets = aisnippets + aisnippet(result)
        return aisnippets
    else:
        # das ist der product prompt
        aisnippets = "Beantworte die Frage '" + query + "' in insgesamt höchstens 50 Wörten auf deutsch mithilfe der Suchergebnisse es geht dabei um den Kauf des in der Suchanfrage stehenden Products:\n\n"
        for _, result in results.iterrows():
            aisnippets = aisnippets + aisnippet(result)
        return aisnippets


def get_ai_summary(results, query, selection) -> str:
    prompt = allsnippet(results, query, selection)

    client = OpenAI(
        # This is the default and can be omitted
        api_key="glpat-yoaOjCxEAJ3z7Zn1WHDDx286MQp1OmR3bQk.01.0z1dn4qi3",
        base_url="https://api.blablador.fz-juelich.de/v1/",
    )
    response = client.responses.create(
        model="alias-fast",
        input=prompt,
    )
    return response.output_text


def highlight_word(word: str) -> str:
    if "€" in word:
        return f"**{word}**"
    else:
        return word


def preis(words: list[str]) -> list[str]:
    words_new = []
    for i, word in enumerate(words):
        if word == "€" and i > 0:
            word = words[i-1] + "€"
            words_new.append(word)
        elif i < len(words)-1 and words[i+1] == "€":
            continue
        else:
            words_new.append(word)
    return words_new


# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir_news, index_dir_products) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)
    set_page_config(
        page_title="All-about-bikes",
        layout="centered",
    )
    image("sommercamp/ChatGPT Image 7. Aug. 2026, 17_41_58.png")

    set_custom_font()
    # Gib der App einen Titel und eine Kurzbeschreibung:
    #title("All-about-bikes")
    # markdown("Suche hier in All-about-bikes:")

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query)
    # eingegeben werden kann.
    query = text_input(
        label="Suche hier in All-about-bikes:",
        placeholder="Suche...",
        value=""
    )

    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.
    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return

    options = ["News", "Products"]
    selection = segmented_control(
        "Wähle:", options, selection_mode="single"
    )

    if selection == "News":
        index_dir = index_dir_news
    else:
        index_dir = index_dir_products

    dense = toggle("KI Suche aktivieren")


    # Öffne den Index.
    index = IndexFactory.of(abspath(index_dir))
    # Initialisiere den Such-Algorithmus.
    searcher = Retriever(
        index,
        wmodel="BM25",
        num_results=10,
    )
    # Initialisiere das Modul, zum Abrufen der Texte.
    text_getter = get_text(index, metadata=["url", "title", "text"])
    # Baue die Such-Pipeline zusammen.
    pipeline = searcher >> text_getter

    if dense:
        # Dense retriver Model laden
        model = SBertBiEncoder('sentence-transformers/all-MiniLM-L6-v2')
        pipeline = (pipeline % 8 >> model.scorer()) ^ pipeline

    # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
    results = pipeline.search(query)


    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    show_ai = toggle("KI Zusammenfassung aktivieren")
    if show_ai:
        ai_summary = get_ai_summary(results, query, selection)
        #markdown(ai_summary)
        with container(border=True):
            subheader("✨ KI generierte Zusammenfassung ✨")
            markdown(ai_summary)

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
    divider()
    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
    


    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
    markdown(f"{len(results)} Suchergebnisse.")

    
    
    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for _, row in results.iterrows():
        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):
            # Speichere den Text in einer Variablen (text).
            text = row["text"]
            # Zeige den Titel der gefundenen Webseite an.
            subheader(get_ai_snippet_titel(text, query))

             # KI-Zusammenfassung für jedes Suchergebnis (immer aktiv)
            with spinner("Erstelle KI-Zusammenfassung..."):
                text = get_ai_snippet_summary(text, query)

            # Schneide den Text nach 500 Zeichen ab.
            # text = text[:500]
            # Ersetze Zeilenumbrüche durch Leerzeichen.
            text = text.replace("\n", " ")

            if selection == "Products":
                words = text.split()
                words = preis(words)
                words = [highlight_word(word) for word in words]
                text = " ".join(words)

            # Zeige den Dokument-Text an.
            markdown(text)
            # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
            link_button("Seite öffnen", url=row["url"])


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.
    index_dir_news = argv[1]
    index_dir_products = argv[2]

    print("Lade News-Index:", index_dir_news)
    print("Lade Product-Index:", index_dir_products)

    # Wenn es noch keinen Index gibt, kannst du die Suchmaschine nicht starten.
    if not exists(index_dir_news) or not exists(index_dir_products):
        print("Index fehlt!!!")
        exit(1)

    # Rufe die App-Funktion von oben auf.
    app(index_dir_news, index_dir_products)


if __name__ == '__main__':
    main()



