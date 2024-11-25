from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)  # Habilitar CORS para todas las rutas
    
    # Configuración básica
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max-limit
    )

    # Registro de rutas
    @app.route('/')
    def index():
        """Ruta principal que renderiza la página inicial"""
        return render_template('index.html')

    @app.route('/health')
    def health_check():
        """Endpoint para verificar el estado del servidor"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })

    @app.errorhandler(404)
    def not_found_error(error):
        """Manejador de errores 404"""
        return jsonify({
            "error": "Recurso no encontrado",
            "status": 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Manejador de errores 500"""
        logger.error(f"Error interno del servidor: {str(error)}")
        return jsonify({
            "error": "Error interno del servidor",
            "status": 500
        }), 500

    @app.after_request
    def after_request(response):
        """Configuración de headers para todas las respuestas"""
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    return app