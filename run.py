from flask import Flask, render_template, request, jsonify
import autogen
from tools import research, write_content
import os
from dotenv import load_dotenv
import logging
from openai import OpenAI
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear el cliente de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuración de OpenAI para autogen
config_list = [{
    "model": "gpt-3.5-turbo",
    "api_key": os.getenv("OPENAI_API_KEY")
}]

# Configuración de funciones para el asistente
llm_config_content_assistant = {
    "functions": [
        {
            "name": "research",
            "description": "Investiga sobre un tema dado y retorna el material de investigación incluyendo enlaces de referencia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "El tema sobre el cual investigar",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "write_content",
            "description": "Escribe contenido basado en el material de investigación y tema proporcionados",
            "parameters": {
                "type": "object",
                "properties": {
                    "research_material": {
                        "type": "string",
                        "description": "Material de investigación sobre un tema dado",
                    },
                    "topic": {
                        "type": "string",
                        "description": "El tema del contenido",
                    }
                },
                "required": ["research_material", "topic"],
            },
        },
    ],
    "config_list": config_list,
    "timeout": 120,
}

def create_agents(brand_task, user_task):
    """Crea y retorna la lista de agentes configurados"""
    agency_manager = autogen.AssistantAgent(
        name="Agency_Manager",
        llm_config={"config_list": config_list},
        system_message=f'''
        Desarrolla tareas paso a paso para {brand_task} y {user_task} con el equipo.
        Actúa como centro de comunicación, mantén entregables de alta calidad.
        Termina la conversación con "TERMINATE" cuando todas las tareas estén completadas.
        '''
    )

    agency_researcher = autogen.AssistantAgent(
        name="Agency_Researcher",
        llm_config=llm_config_content_assistant,
        system_message=f'''
        Utiliza la función de investigación para recopilar información relevante.
        Enfócate en entregar información clara y procesable.
        Concluye con "TERMINATE" una vez que la investigación esté completa.
        '''
    )
    agency_researcher.register_function(
        function_map={
            "research": research
        }
    )

    agency_strategist = autogen.AssistantAgent(
        name="Agency_Strategist",
        llm_config={"config_list": config_list},
        system_message=f'''
        Desarrolla informes estratégicos para {brand_task}, guiado por {user_task}.
        Utiliza los conocimientos del Agency_Researcher para informar estrategias.
        Concluye con "TERMINATE" una vez que la dirección estratégica esté establecida.
        '''
    )

    agency_writer = autogen.AssistantAgent(
        name="Agency_Copywriter",
        llm_config={"config_list": config_list},
        system_message="""
        Crea contenido y narrativas atractivas alineadas con los objetivos.
        Enfócate en mensajes claros y relevantes.
        Concluye con "TERMINATE" cuando el contenido esté completo.
        """,
        function_map={
            "write_content": write_content,
        },
    )

    writing_assistant = autogen.AssistantAgent(
        name="writing_assistant",
        llm_config=llm_config_content_assistant,
        system_message="""
        Asiste en investigación y creación de contenido.
        Produce material informativo y bien estructurado.
        Concluye con "TERMINATE" después de completar las tareas.
        """,
        function_map={
            "research": research,
            "write_content": write_content,
        },
    )

    agency_marketer = autogen.AssistantAgent(
        name="Agency_Marketer",
        llm_config={"config_list": config_list},
        system_message=f'''
        Desarrolla estrategias de marketing para {user_task}.
        Crea campañas que comuniquen el valor de la marca.
        Concluye con "TERMINATE" cuando las estrategias estén completas.
        '''
    )

    agency_mediaplanner = autogen.AssistantAgent(
        name="Agency_Media_Planner",
        llm_config={"config_list": config_list},
        system_message=f'''
        Identifica canales óptimos para la entrega de publicidad.
        Formula estrategias efectivas para alcanzar la audiencia.
        Concluye con "TERMINATE" una vez que la planificación esté completa.
        '''
    )

    agency_director = autogen.AssistantAgent(
        name="Agency_Director",
        llm_config={"config_list": config_list},
        system_message="""
        Supervisa la calidad creativa del proyecto.
        Asegura originalidad y excelencia en todas las ideas.
        Concluye con "TERMINATE" una vez asegurada la integridad creativa.
        """,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda msg: "TERMINATE" in msg["content"] if msg["content"] else False,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={
            "work_dir": "logs",
            "use_docker": False
        },
        system_message='Sé un asistente útil y comunícate siempre en español.',
    )

    return [user_proxy, agency_manager, agency_researcher, agency_strategist, 
            agency_writer, writing_assistant, agency_marketer, agency_mediaplanner, 
            agency_director]
def format_strategy(messages):
    """Formatea los mensajes del chat en una estrategia estructurada"""
    strategy = {
        "resumen": "",
        "pasos": [],
        "recomendaciones": [],
        "investigacion": [],
        "plan_medios": [],
        "contenido": []
    }
    
    for msg in messages:
        try:
            content = str(msg.get("content", ""))
            name = msg.get("name", "").lower()
            
            if "manager" in name and ("resumen" in content.lower() or "ejecutivo" in content.lower()):
                strategy["resumen"] = content
            elif "strategist" in name:
                strategy["pasos"].append(content)
            elif "marketer" in name:
                strategy["recomendaciones"].append(content)
            elif "researcher" in name and not content.startswith("None"):
                strategy["investigacion"].append(content)
            elif "media" in name:
                strategy["plan_medios"].append(content)
            elif "copywriter" in name:
                strategy["contenido"].append(content)
        except Exception as e:
            logger.error(f"Error formateando mensaje: {str(e)}")
            continue
    
    return strategy

# Agregar la ruta raíz
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        brand_task = data.get('brandTask')
        user_task = data.get('userTask')
        
        logger.info(f"Iniciando análisis para marca: {brand_task}, objetivo: {user_task}")
        
        if not brand_task or not user_task:
            return jsonify({
                "success": False,
                "error": "Se requieren tanto la marca como el objetivo"
            }), 400
        
        # Crear agentes y configurar el chat
        agents = create_agents(brand_task, user_task)
        groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=20)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})
        
        # Iniciar chat y capturar la conversación
        user_proxy = agents[0]
        
        # Prompt más estructurado
        prompt = f"""
        Como equipo, necesitamos desarrollar una estrategia de marketing completa para {brand_task} 
        con el objetivo de {user_task}.

        Agency_Manager: Coordina el proceso y proporciona un resumen ejecutivo.
        Agency_Researcher: Investiga el mercado y la competencia.
        Agency_Strategist: Desarrolla la estrategia y pasos de acción.
        Agency_Marketer: Proporciona recomendaciones de marketing específicas.
        Agency_Media_Planner: Desarrolla el plan de medios.
        Agency_Copywriter: Crea el contenido propuesto.

        Por favor, trabajen juntos para crear una estrategia completa.
        """
        
        logger.info("Iniciando chat con el prompt estructurado")
        
        # Iniciar el chat sin callback
        user_proxy.initiate_chat(
            manager,
            message=prompt
        )
        
        # Obtener mensajes directamente del groupchat
        chat_history = []
        for message in groupchat.messages:
            if isinstance(message, dict) and message.get("content"):
                content = message.get("content")
                name = message.get("name", "Sistema")
                if not content.startswith("***** Suggested function call"):
                    chat_history.append({
                        "role": message.get("role", "assistant"),
                        "content": content,
                        "name": name
                    })
                    logger.info(f"Mensaje agregado de {name}: {content[:100]}...")
        
        logger.info(f"Chat finalizado. Total de mensajes: {len(chat_history)}")
        
        # Formatear y enviar respuesta
        strategy = format_strategy(chat_history)
        logger.info(f"Estrategia formateada: {strategy}")
        
        # Verificar si hay contenido
        has_content = any([
            strategy["resumen"],
            strategy["pasos"],
            strategy["recomendaciones"],
            strategy["investigacion"],
            strategy["plan_medios"],
            strategy["contenido"]
        ])
        
        logger.info(f"¿La estrategia tiene contenido? {has_content}")
        
        if not has_content:
            logger.warning("No se generó contenido en la estrategia")
            return jsonify({
                "success": False,
                "error": "No se pudo generar la estrategia"
            }), 500
        
        final_response = {
            "success": True,
            "strategy": strategy
        }
        
        return jsonify(final_response)
        
    except Exception as e:
        logger.error(f"Error en el análisis: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error en el procesamiento: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Configuración simple para desarrollo local
    app.run(debug=True)