import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import folium
from folium.plugins import HeatMapWithTime, TimestampedGeoJson
from datetime import datetime, timedelta

# -----------------------------
# 0. Configuración
# -----------------------------
np.random.seed(42)

# Zonas (coordenadas aproximadas en Madrid)
ZONES = {
    "Centro": (40.4168, -3.7038),
    "Retiro": (40.4110, -3.6760),
    "Chamartín": (40.4670, -3.6890),
    "Salamanca": (40.4297, -3.6789),
    "Arganzuela": (40.3989, -3.7030),
    "Usera": (40.3859, -3.6995),
    "Moncloa": (40.4358, -3.7183),
}

# -----------------------------
# 1. Simulación de evento cultural con propagación
# -----------------------------
start_time = datetime(2025, 11, 15, 18, 0)  # inicio del evento (concierto)
hours = 6  # duración de observación
time_points = [start_time + timedelta(hours=h) for h in range(hours + 1)]

# Generar "posts" por hora y zona con una ola que parte de Centro y Retiro
rows = []
for t in time_points:
    for zone, (lat, lon) in ZONES.items():
        # Intensidad base decrece con la distancia temporal al inicio
        base_intensity = max(0, 1 - (t - start_time).total_seconds() / (hours * 3600))
        # Centro y Retiro activan antes; el resto se “enciende” con retraso según orden
        zone_delay = {
            "Centro": 0,
            "Retiro": 1,
            "Salamanca": 2,
            "Chamartín": 2,
            "Arganzuela": 3,
            "Moncloa": 3,
            "Usera": 4,
        }[zone]
        active = (t - start_time).total_seconds() >= zone_delay * 3600
        intensity = (base_intensity * (1 if active else 0)) + np.random.normal(0.05, 0.03)
        intensity = float(np.clip(intensity, 0, 1))
        # Simular textos (evento vs quejas transporte)
        if active and np.random.rand() < 0.75:
            text = f"Gran concierto cerca de {zone}, ¡qué ambiente!"
        else:
            text = f"Retrasos en el transporte por afluencia cerca de {zone}"
        rows.append({
            "text": text,
            "zone": zone,
            "lat": lat + np.random.normal(0, 0.001),  # jitter leve
            "lon": lon + np.random.normal(0, 0.001),
            "time": t,
            "intensity": intensity
        })

df = pd.DataFrame(rows)

# -----------------------------
# 2. Sentimiento y temas (NMF)
# -----------------------------
def sentiment_score(text):
    return TextBlob(text).sentiment.polarity

df["sentiment"] = df["text"].apply(sentiment_score)

vectorizer = TfidfVectorizer(stop_words="spanish")
X = vectorizer.fit_transform(df["text"])
nmf = NMF(n_components=2, random_state=42)
W = nmf.fit_transform(X)
df["topic_id"] = W.argmax(axis=1)
topic_labels = {0: "Eventos/Cultura", 1: "Transporte/Movilidad"}
df["topic_label"] = df["topic_id"].map(topic_labels)

# -----------------------------
# 3. Agregación por hora y zona para KPIs
# -----------------------------
agg = df.groupby(["zone", pd.Grouper(key="time", freq="H")]).agg(
    avg_sentiment=("sentiment", "mean"),
    intensity=("intensity", "mean"),
    posts=("text", "count"),
    event_share=("topic_label", lambda s: (s == "Eventos/Cultura").mean())
).reset_index()

# Métricas de propagación:
# - time_to_peak: hora desde inicio hasta pico de intensidad por zona
# - coverage: zonas con pico > umbral
# - spread_speed: tiempo medio entre primeras activaciones de zonas
peaks = agg.loc[agg.groupby("zone")["intensity"].idxmax()]
peaks["time_to_peak_h"] = (peaks["time"] - start_time).dt.total_seconds() / 3600.0
threshold = 0.4
coverage = (peaks["intensity"] > threshold).mean()  # proporción de zonas impactadas
first_activation = agg[agg["intensity"] > 0.2].groupby("zone")["time"].min().sort_values()
if len(first_activation) > 1:
    diffs = first_activation.diff().dropna().dt.total_seconds() / 3600.0
    spread_speed_h = float(diffs.mean())
else:
    spread_speed_h = 0.0

print(f"KPIs -> coverage: {coverage:.2f}, spread_speed (h): {spread_speed_h:.2f}")

# -----------------------------
# 4. Mapa base
# -----------------------------
m = folium.Map(location=[40.4168, -3.7038], zoom_start=12)

# -----------------------------
# 5. HeatMap temporal (sentimiento como peso)
# -----------------------------
# Construir capas por cada instante (lista de [lat, lon, weight])
time_sorted = sorted(df["time"].unique())
heat_series = []
for t in time_sorted:
    slice_df = df[df["time"] == t]
    # Usamos sentimiento normalizado a [0,1] como peso visual
    w = (slice_df["sentiment"] - slice_df["sentiment"].min()) / (slice_df["sentiment"].max() - slice_df["sentiment"].min() + 1e-9)
    points = [[row["lat"], row["lon"], float(w.iloc[i])] for i, row in slice_df.iterrows()]
    heat_series.append(points)

HeatMapWithTime(
    data=heat_series,
    index=[ts.strftime("%Y-%m-%d %H:%M") for ts in time_sorted],
    radius=30,
    auto_play=True,
    max_opacity=0.8,
    use_local_extrema=False
).add_to(m)

# -----------------------------
# 6. Timeline de eventos (TimestampedGeoJson)
# -----------------------------
features = []
for _, r in df.iterrows():
    color = "#1f78b4" if r["topic_label"] == "Eventos/Cultura" else "#e31a1c"
    popup = f"{r['topic_label']} | Sent: {r['sentiment']:.2f} | {r['zone']} | {r['time'].strftime('%H:%M')}"
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
        "properties": {
            "time": r["time"].isoformat(),
            "style": {"color": color, "fillColor": color, "fillOpacity": 0.7, "weight": 2},
            "icon": "circle",
            "popup": popup
        }
    })

TimestampedGeoJson({
    "type": "FeatureCollection",
    "features": features
}, period="PT1H", add_last_point=True, auto_play=False, loop=False, duration="PT1M").add_to(m)

# -----------------------------
# 7. Indicadores resumen en popup por zona (picos e intensidad)
# -----------------------------
for zone, (lat, lon) in ZONES.items():
    z = peaks[peaks["zone"] == zone]
    if not z.empty:
        text = f"""
        <b>{zone}</b><br>
        Pico intensidad: {z['intensity'].values[0]:.2f}<br>
        Time-to-peak (h): {z['time_to_peak_h'].values[0]:.2f}<br>
        Share evento: {agg[(agg['zone']==zone)]['event_share'].mean():.2f}
        """
    else:
        text = f"<b>{zone}</b><br>Sin activación relevante"
    folium.Marker(
        location=(lat, lon),
        popup=folium.Popup(text, max_width=250),
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)

# -----------------------------
# 8. Guardar
# -----------------------------
m.save("pulso_social_urbano_timeline.html")
print("Mapa animado generado: pulso_social_urbano_timeline.html")
