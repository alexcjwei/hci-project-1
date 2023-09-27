# hci-project-1

Code for HCI Project 1 Fall 2023.

## Team
Nick Yuseong Oh
Joe Li
Alex Wei


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