# hci-project-1

Code for HCI Project 1 Fall 2023.

## Team
* Nick Yuseong Oh
* Joe Li
* Alex Wei

## Project Structure
The important files for the project are below.
```
.
├── app.py              # the Alexa skill handler
├── buildspec.yml       # build specs for AWS CodeBuild
├── models              # the Interaction Models
│   └── en-US.json
├── skill.json          # Skill manifest
```

The Alexa skill handler is defined in `app.py`.

We keep a version of the Interaction Model in `models/en-US.json`.


## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Deployment
Merge a PR to `main`. AWS CodeBuild will pick up on the source change and build the project.
After that, the build project updates the AWS Lambda function code, which serves as the Alexa Skill endpoint.


## Reference
* [Alexa Skills Kit SDK For Python Reference](https://alexa-skills-kit-python-sdk.readthedocs.io/en/latest/api/)
* [openai-python](https://github.com/openai/openai-python)