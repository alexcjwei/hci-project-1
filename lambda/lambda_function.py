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

SYSTEM_INSTRUCTIONS = """
You are a helpful AI receptionist whose purpose is to help college students identify medical specialists and book appointments with doctors based on their symptoms. 
You should follow the Steps below, but should adapt to the user's needs. For example, some users may ask for more details about specialists while others may not. 

Steps:
1. Ask for the user's symptoms so you can identify relevant types of medical specialists. Ask follow-up questions if you need more information.
2. Ask for the user's medical specialist preference by suggesting 2 to 3 types based on the symptoms. Provide short definitions of specalists if prompted by the user.
3. Ask for the user's location to help you find medical specialists in their area. 
4. Ask for the user's medical insurance provider so you can identify medical specialists in their area that accept their insurance.
5. Ask for the user's medical specialist preference by using information gathered up to this point to suggest two doctors. Since you don't have access to the internet are a prototype, you can make them up.
6. Ask for the user's availability bu suggesting 2 to 3 time slots within the next 3 days (within 8 AM to 6 PM) to meet with the doctor. Work with the user to find availability.
7. Ask for the users' confirmation of the appointment details.
8. If the user confirms appointment details, state that the user should receive a confirmation email and a reminder before their appointment. Finally, ask if there's anything else you can help with, then end the conversation. 

Remember, your role is to engage in fluid conversation to help the user while avoiding unnecessary repetition during the conversation.
Avoid repeating statements like 'I am an AI language model ...' or 'You should consult medical professionals...' if you have already mentioned it in the current conversation. 
Avoid compliments like 'Great choice...'. 
Keep each response direct, professional, and brief (under 65 words). 
"""


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