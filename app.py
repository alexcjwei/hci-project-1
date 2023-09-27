from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
import os
import openai
from dotenv import load_dotenv

load_dotenv()

sb = SkillBuilder()
openai.api_key = os.getenv('OPENAI_API_KEY')

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input: HandlerInput) -> Response:
    speech_text: str = "Welcome to the Alexa Skills Kit, you can say hello!"

    handler_input.response_builder.speak(speech_text).set_should_end_session(
        False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("AskChatGPTIntent"))
def ask_chat_gpt_intent_handler(handler_input: HandlerInput) -> Response:
    question = handler_input.request_envelope.request.intent.slots['question'].value

    # See https://platform.openai.com/docs/api-reference/chat/create 
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a dog."}, # The prompt
            {"role": "user", "content": question},
        ]
    )

    speech_text = response.choices[0].message.content

    handler_input.response_builder.speak(speech_text).set_should_end_session(
        False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input: HandlerInput) -> Response:
    speech_text: str = "Help intent handler here!"

    handler_input.response_builder.speak(speech_text).ask(speech_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input: HandlerInput) -> Response:
    speech_text: str = "Goodbye!"

    handler_input.response_builder.speak(speech_text).set_should_end_session(
            True)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input: HandlerInput) -> Response:
    # Cleanup?
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input: HandlerInput, exception: Exception) -> Response:
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Sorry, I didn't get it. Can you please say it again?"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


handler = sb.lambda_handler()