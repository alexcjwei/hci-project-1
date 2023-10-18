# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the decorators approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

import openai

sb = SkillBuilder()
openai.api_key = 'test'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Currently working GPT responses, but need to move on to finding specific specialties 
@sb.request_handler(can_handle_func=is_intent_name("SymptomReporting"))
def report_symptom_request_handler(handler_input: HandlerInput) -> Response:
    request = handler_input.request_envelope.request
    spoken_text = handler_input.request_envelope.request.intent.slots['symptoms'].value

    session_attr = handler_input.attributes_manager.session_attributes
    
    # Check if 'messages' key exists in session attributes
    if 'messages' not in session_attr:
        session_attr['messages'] = []

    session_attr['messages'].append({"role": "user", "content": spoken_text})

    # Append user's and previous assistant's messages for OpenAI context
    messages = session_attr['messages']

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        speech_text = response.choices[0].message.content
        session_attr['messages'].append({"role": "assistant", "content": speech_text})

    except Exception as e:
        # Log the actual error message to help in debugging
        logger.error(f"Error occurred: {str(e)}")
        # Send a generic error message to the user
        speech_text = "Sorry, I encountered an error. Please try again later."


    # Keeping the session open for further interaction
    handler_input.response_builder.speak(speech_text).ask(speech_text)
    
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response

    # Initialize or reset the messages in session attributes
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['messages'] = []

    # Updated speech text
    speech_text = "Hello! If you're feeling unwell, tell me your symptoms and I can suggest some medical specialists you might consider seeing."

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Medical Specialist Assistant", speech_text)).set_should_end_session(
        False).response


@sb.request_handler(can_handle_func=is_intent_name("HelloWorldIntent"))
def hello_world_intent_handler(handler_input):
    """Handler for Hello World Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Hello Python World from Decorators!"

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).set_should_end_session(
        True).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "You can say hello to me!"

    return handler_input.response_builder.speak(speech_text).ask(
        speech_text).set_card(SimpleCard(
            "Hello World", speech_text)).response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Hello World skill can't help you with that.  "
        "You can say hello!!")
    reprompt = "You can say hello!!"
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


lambda_handler = sb.lambda_handler()