import base64
import os


# --- Hier deine Funktionen einfügen ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
# --- Ende der Funktionen ---

# Funktion aufrufen, bevor der Rest deiner App startet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bild_pfad = os.path.join(BASE_DIR, 'background.png')

set_png_as_page_bg(bild_pfad)




words = text.split()

            if selection == "Products":
                words = preis(words)
                words = [highlight_word(word) for word in words]

            words = words[:50]            # nur die ersten 50 Wörter behalten
            text = " ".join(words)        # wieder zu einem Text zusammensetzen