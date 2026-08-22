import json
import logging
import os
import urllib.request
import urllib.error

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_MODEL = "gemini-3.5-flash-lite"


def get_gemini_response(user_query):
    clean_key = GEMINI_API_KEY.strip()

    if not clean_key:
        logger.error("GEMINI_API_KEY não está definida como variável de ambiente.")
        return "A chave da API não foi configurada corretamente no servidor."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={clean_key}"

    prompt = (
        "Você é a assistente de voz Bolha Pessoal rodando na Alexa. "
        "Responda em português de forma sucinta, direta e em no máximo 3 frases. "
        "Não use formatação Markdown nem emojis.\n\n"
        f"Pergunta: {user_query}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
            "thinkingConfig": {"thinkingLevel": "minimal"}
        }
    }

    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=7) as response:
            res_json = json.loads(response.read().decode('utf-8'))

            candidates = res_json.get('candidates')
            if not candidates:
                motivo = res_json.get('promptFeedback', {}).get('blockReason', 'desconhecido')
                logger.error(f"Nenhum candidato retornado pela API. blockReason: {motivo}")
                return "Não consegui gerar uma resposta para essa pergunta."

            parts = candidates[0].get('content', {}).get('parts')
            if not parts:
                finish_reason = candidates[0].get('finishReason', 'desconhecido')
                logger.error(f"Resposta sem texto. finishReason: {finish_reason}")
                return "Não consegui gerar uma resposta para essa pergunta."

            return parts[0]['text'].strip()
    except urllib.error.HTTPError as e:
        err_message = e.read().decode('utf-8')
        logger.error(f"HTTP Error {e.code}: {err_message}")
        return f"Erro do Google número {e.code}."
    except Exception as ex:
        logger.error(f"Erro geral: {ex}")
        return "Desculpe, ocorreu uma falha de conexão."


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Modo Bolha Pessoal ativado. O que você gostaria de perguntar?"
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class AskGptIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AskGptIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        user_query = None

        if slots:
            for slot_key in ["bolha_pessoal", "bolha", "pessoal", "query"]:
                if slot_key in slots and slots[slot_key].value:
                    user_query = slots[slot_key].value
                    break
            if not user_query:
                for slot in slots.values():
                    if slot.value:
                        user_query = slot.value
                        break

        if not user_query:
            speak_output = "Não entendi sua pergunta. Pode repetir?"
            return handler_input.response_builder.speak(speak_output).ask(speak_output).response

        speak_output = get_gemini_response(user_query)

        return handler_input.response_builder.speak(speak_output).ask("Mais alguma dúvida?").response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak("Você pode me fazer qualquer pergunta.").response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        return handler_input.response_builder.speak("Até logo!").response


class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.speak("Não entendi direito.").response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        return handler_input.response_builder.speak("Ocorreu um erro interno.").response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskGptIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
