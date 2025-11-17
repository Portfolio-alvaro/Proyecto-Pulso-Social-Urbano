Timeline animada de eventos con TimestampedGeoJson.

Heatmap temporal con HeatMapWithTime.

KPIs de propagación (velocidad y cobertura) calculados sobre ventanas temporales.

Qué obtienes
Heatmap con evolución temporal: verás cómo cambia el sentimiento a lo largo de las horas del evento.

Timeline de puntos por tema: cada post aparece en su momento, coloreado por “Eventos/Cultura” vs “Transporte/Movilidad”.

KPIs de propagación: cobertura de zonas impactadas y velocidad media de expansión.
Roadmap visual (timeline conceptual) 


📍 Fase 1: MVP funcional (2–3 semanas)
Ingesta básica: scraping con snscrape y filtros por ciudad/hashtags.

Procesamiento inicial: análisis de sentimiento con VADER/TextBlob.

Clustering de temas: NMF sobre TF‑IDF para identificar categorías.

Geolocalización simple: geopy + agregación por distrito.

Dashboard inicial: mapas choropleth y heatmaps interactivos con Leaflet/Folium.

Persistencia: Postgres con índices básicos.

Infraestructura: API Flask y despliegue con Docker Compose.

📍 Fase 2: Robustez y diagnóstico (3–4 semanas)
Clasificador supervisado de quejas: entrenado con dataset etiquetado (transporte, cultura, seguridad).

Propagación de eventos: timeline animada con TimestampedGeoJson y KPIs de difusión.

Feature store: repositorio centralizado de variables derivadas para consistencia.

Model registry: versionado semántico de modelos econométricos con rollback.

Monitoring y drift detection: métricas de rendimiento, distribución de features y alertas.

Explicabilidad: integración de SHAP/LIME y análisis de sensibilidad para transparencia.

📍 Fase 3: Escalado y simulación (4+ semanas)
Microservicios con auto‑scaling: despliegue en contenedores independientes para ingesta, API y dashboard.

Simulaciones Monte Carlo: huella digital de temas (#ClimateChange) en escenarios urbanos.

Optimización de consultas: agregados incrementales y cache geojson para rendimiento.

Governance avanzado: trazabilidad completa, reproducibilidad, auditorías de sesgo y cumplimiento ético.

Dashboard enriquecido: KPIs estratégicos, simulaciones temáticas y visualización comparativa entre escenarios.

✅ Claves del roadmap
Fase 1: entregar un prototipo funcional y reproducible.

Fase 2: robustecer el sistema con diagnóstico avanzado y explicabilidad.

Fase 3: escalar hacia simulaciones y gobernanza ética, con visión empresarial.
