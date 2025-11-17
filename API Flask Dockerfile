# Imagen base ligera de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API
COPY . .

# Exponer el puerto de la API
EXPOSE 8080

# Comando de arranque con Gunicorn
# -b 0.0.0.0:8080 → escucha en todas las interfaces
# -w 4 → 4 workers para concurrencia
# app:app → nombre del archivo (app.py) y objeto Flask
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "app:app"]
