# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf ~/.cache/pip

# Copiar el resto del proyecto
COPY . /app

# Exponer el puerto que usará Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación en el puerto 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
