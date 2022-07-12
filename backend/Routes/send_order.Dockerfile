FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./send_order.py ./invokes.py ./amqp_email_setup.py ./key.json ./
CMD [ "python", "./send_order.py" ]