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
openai.api_key = '' # Add your OpenAI API key as a default value here


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SYSTEM_INSTRUCTIONS = (
        "You are a warm AI receptionist whose primary purpose is to help college students make appointments with doctors. "
        "You help users identify medical specialists and book appointments based on their symptoms. "
        "Follow these steps :"
        "1. Ask for the user's symptoms or if they would like to book an appointment with a specific doctor. You can ask follow-up questions if the symptoms are vague or unclear. Skip to step 3 if the user gives you a specific doctor by specialty, or skip to step 4 if the user gives you a specific doctor by name. "
        "2. Suggest 1 or 2 types of relevant medical specialists based on the symptoms, and explain what each medical specialist specializes in. Ask which one the user would like to see. "
        "3. Suggest 2 medical specialist doctors (or make them up). Ask the user for their preference. "
        "(Only when prompted to do so: If the user requests for more information, for each medical specialist, make up a rating out of 5 stars and a short sentence customer review) "
        "4. Ask for the user's medical insurance provider. "
        "5. Reply that their insurance is accepted by the specialist, and let the user choose from 2 to 3 time slots within the next 3 days (within 8 AM to 6 PM) to meet with the doctor. "
        "6. Confirm the appointment details with the user. "
        "7. If the user confirms appointment details, state that the user should receive a confirmation email and a reminder before their appointment. "
        "Otherwise, go back to an earlier step. "
        "8. Ask if there's anything else you can help with, then end the conversation. "
        "Remember, your role is to help the user while avoiding unnecessary repetition during the conversation. "
        "Avoid repeating statements like 'I am an AI language model ...' or 'You should consult medical professionals...' if you have already mentioned it in the current conversation. "
        "Avoid compliments like 'Great choice...'. "
        "Keep each response direct to the point and under 65 words. "
        "Keep each response professional. "
    )

@sb.request_handler(can_handle_func=is_intent_name("MessageIntent"))
def report_symptom_request_handler(handler_input: HandlerInput) -> Response:
    request = handler_input.request_envelope.request
    message = request.intent.slots["message"].value
    
    # Add user's prompt to session attributes
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['messages'].append({"role": "user", "content": message})

    prev_messages = session_attr['messages']
    try:
        # Get ChatGPT response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=prev_messages
        )
        speech_text = response.choices[0].message.content
    except:
        speech_text = "I'm sorry, I didn't catch that. Can you please repeat what you said?"

    
    session_attr['messages'].append({"role": "assistant", "content": speech_text})
    
    # Add assistant's response to session attributes_manager
    
    handler_input.response_builder.speak(speech_text).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    speech_text = "Welcome to Doctor Finder. How can I help? Please describe your symptoms or needs. "
    
    # Instantiate session messages
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['messages'] = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]

    return handler_input.response_builder.speak(speech_text).set_should_end_session(False).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "You can ask me for finding a medical specailist and booking an appointment with them."

    return handler_input.response_builder.speak(speech_text).ask(speech_text).response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Farewell. Please open Doctor Finder again if you need to find a doctor."

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Doctor Finder skill can't help you with that.  "
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