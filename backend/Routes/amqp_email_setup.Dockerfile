FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./amqp_email_setup.py .
CMD [ "python", "./amqp_email_setup.py"]