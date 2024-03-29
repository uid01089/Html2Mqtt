FROM arm64v8/python:3.12-alpine

# Update system
RUN apk update && apk upgrade

# Create workdir
WORKDIR /app

# Setup requirements, no venv needed
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy app itself
COPY . .

# Call script
# CMD [ "gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "Html2Mqtt:create_app" ]
CMD [ "python", "./Html2Mqtt.py" ]
