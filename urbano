import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import folium
from folium.plugins import HeatMap
import datetime

# -----------------------------
# 1. Datos simulados (tweets)
# -----------------------------
data = [
    {"text": "Me encanta el concierto en el centro, mucha alegría!", "location": "Madrid Centro", "time": "2025-11-15 21:00"},
    {"text": "El transporte público está fatal hoy, retrasos y quejas", "location": "Madrid Sur", "time": "2025-11-15 08:30"},
    {"text": "Gran evento cultural en Retiro, mucha gente comentando", "location": "Madrid Retiro", "time": "2025-11-15 19:00"},
    {"text": "El tráfico en Chamartín es insoportable", "location": "Madrid Chamartín", "time": "2025-11-15 09:00"},
]

df = pd.DataFrame(data)
df["time"] = pd.to_datetime(df["time"])

# -----------------------------
# 2. Análisis de sentimiento
# -----------------------------
def sentiment_score(text):
    return TextBlob(text).sentiment.polarity

df["sentiment"] = df["text"].apply(sentiment_score)

# -----------------------------
# 3. Clasificación de temas (NMF)
# -----------------------------
vectorizer = TfidfVectorizer(stop_words="spanish")
X = vectorizer.fit_transform(df["text"])
nmf = NMF(n_components=2, random_state=42)
topics = nmf.fit_transform(X)

df["topic_id"] = topics.argmax(axis=1)
topic_labels = {0: "Transporte/Ciudad", 1: "Eventos/Cultura"}
df["topic_label"] = df["topic_id"].map(topic_labels)

# -----------------------------
# 4. Geolocalización simulada
# -----------------------------
geo_coords = {
    "Madrid Centro": (40.4168, -3.7038),
    "Madrid Sur": (40.345, -3.709),
    "Madrid Retiro": (40.411, -3.676),
    "Madrid Chamartín": (40.467, -3.689),
}
df["coords"] = df["location"].map(geo_coords)

# -----------------------------
# 5. Mapa interactivo con Folium
# -----------------------------
m = folium.Map(location=[40.4168, -3.7038], zoom_start=12)

# Heatmap de sentimiento
heat_data = [[row["coords"][0], row["coords"][1], row["sentiment"]] for _, row in df.iterrows()]
HeatMap(heat_data, radius=25).add_to(m)

# Marcadores con tema
for _, row in df.iterrows():
    folium.Marker(
        location=row["coords"],
        popup=f"{row['text']} | Sentiment: {row['sentiment']:.2f} | Tema: {row['topic_label']}",
        icon=folium.Icon(color="blue" if row["topic_label"] == "Eventos/Cultura" else "red")
    ).add_to(m)

# Guardar mapa
m.save("pulso_social_urbano.html")
print("Mapa generado: pulso_social_urbano.html")
