# Hier importieren wir die benötigten Softwarebibliotheken.
from os.path import abspath, exists
from sys import argv
from streamlit import (
    text_input, header, title, subheader, container,
    markdown, link_button, divider, set_page_config, segmented_control)
from pyterrier import IndexFactory
from pyterrier.terrier import Retriever
from pyterrier.text import get_text


def snippet_ai(result) -> str:
    snippet_lines = [
        "Titel: " + result["title"],
        "Url: " + result["url"],
        "Text: " + result["text"].replace("\n", " ")
        ]
    return "\n".join(snippet_lines)


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

    # Gib der App einen Titel und eine Kurzbeschreibung:
    title("All-about-bikes")
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
    # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
    results = pipeline.search(query)

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
    divider()
    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
    markdown(f"{len(results)} Suchergebnisse.")

    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for _, row in results.iterrows():
        print(snippet_ai(row))
        # exit()

        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):
            # Zeige den Titel der gefundenen Webseite an.
            subheader(row["title"])
            # Speichere den Text in einer Variablen (text).
            text = row["text"]
            words = text.split()

            if selection == "Products":
                words = preis(words)
                words = [highlight_word(word) for word in words]

            words = words[:50]            # nur die ersten 50 Wörter behalten
            text = " ".join(words)        # wieder zu einem Text zusammensetzen

            # Schneide den Text nach 500 Zeichen ab.
            # text = text[:500]
            # Ersetze Zeilenumbrüche durch Leerzeichen.
            text = text.replace("\n", " ")
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
    print("Hallo")
    main()
