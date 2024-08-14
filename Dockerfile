FROM python:3.12.2

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /GOOGLECHAT

# Copia el archivo de requisitos e instala las dependencias de Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY ventas.csv ventas.csv
COPY main.py main.py
COPY templates/ templates/
COPY static/ static/


# Crear un usuario no root para ejecutar la aplicación
RUN useradd -m app && echo "app ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Cambiar al usuario no root
USER app

# Establece la variable de entorno para la clave API
ENV GOOGLE_API_KEY=AIzaSyDfSpz5qURAUscKqtyx8qJ-x-c1QX2v3pM

# Comando para iniciar la aplicación
ENTRYPOINT ["python", "main.py"]
