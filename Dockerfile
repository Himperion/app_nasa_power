# Usar una imagen base de Python
FROM python:3.11-slim

# evitar buffering de Python en logs
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential \
 && pip install --upgrade pip \
 && pip install -r requirements.txt \
 && apt-get remove -y gcc build-essential \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto que usará Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación en el puerto 8501
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableCORS=false"]
