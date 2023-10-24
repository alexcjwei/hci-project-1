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
openai.api_key = # Add your OpenAI API key as a default value here

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SYSTEM_INSTRUCTIONS = (
        "You are a warm receptionist whose primary purpose is to help college students make appointments with doctors. "
        "You help users identify medical specialists and book appointments based on their symptoms. "
        "Follow these steps:"
        "1. Ask for the user's symptoms. Get as much information as you can by asking follow-up questions if the symptoms are vague or unclear. "
        "2. Suggest 2 to 3 types of relevant medical specialists based on the symptoms, and ask which one the user would like to see. "
        "3. Ask for the user's location to help you find medical specialists in their area. "
        "4. Suggest (or make up) 1 to 2 medical specialists in their area. Ask the user for their preference. "
        "The user may ask for reviews on the practitioner, in which case just make up a rating out of 5 stars. "
        "5. Ask for the user's medical insurance provider. "
        "6. Reply that their insurance is accepted by the specialist, and let the user choose from 2 to 3 time slots to meet with the doctor. "
        "7. Confirm the appointment details with the user. "
        "8. If the user confirms appointment details, state that the user should receive a confirmation email and a reminder before their appointment. "
        "Otherwise, go back to an earlier step. "
        "9. Ask if there's anything else you can help with, then end the conversation. "
        "Remember, your role is to help the user while avoiding unnecessary repetition during the conversation. "
        "Avoid repeating statements like 'I am an AI language model ...' or 'You should consult medical professionals...' if you have already mentioned it in the current conversation. "
        "Keep your response brief."
    )

@sb.request_handler(can_handle_func=is_intent_name("MessageIntent"))
def report_symptom_request_handler(handler_input: HandlerInput) -> Response:
    request = handler_input.request_envelope.request
    message = request.intent.slots["message"].value
    
    # Add user's prompt to session attributes
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['messages'].append({"role": "user", "content": message})

    # question = handler_input.request_envelope.request.intent.slots['symptoms'].value

    prev_messages = session_attr['messages']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prev_messages
    )
    
    speech_text = response.choices[0].message.content
    session_attr['messages'].append({"role": "assistant", "content": speech_text})
    
    # Add assistant's response to session attributes_manager
    
    handler_input.response_builder.speak(speech_text).set_should_end_session(False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    speech_text = "How can I help? Please describe the purpose of your appointment. "
    
    # Instantiate session messages
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['messages'] = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "assistant", "content": speech_text},
    ]

    return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "You can ask me for help booking an appointment with a doctor."

    return handler_input.response_builder.speak(speech_text).ask(speech_text).response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Doctor Appointment Scheduler skill can't help you with that.  "
        "You can ask for help booking an appointment.")
    reprompt = "You can ask for help booking an appointment."
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

    speech = "Sorry, there was some problem. Please try again."
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


lambda_handler = sb.lambda_handler()