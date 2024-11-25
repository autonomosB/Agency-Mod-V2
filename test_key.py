from openai import OpenAI
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Crear el cliente de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    # Hacer una llamada simple a la API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hola, esta es una prueba."}
        ]
    )
    print("La clave API funciona correctamente!")
    print("Respuesta:", response.choices[0].message.content)
except Exception as e:
    print("Error con la clave API:", str(e))