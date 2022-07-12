FROM python:3-slim
WORKDIR ESDTelemedicine/backend
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./google_login.py ./key.json ./
CMD [ "python", "./google_login.py"]