# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto que usará Streamlit
EXPOSE 8080

# Comando para ejecutar la aplicación en el puerto 8080
CMD ["streamlit", "run", "main.py", "--server.port", "8080"]
