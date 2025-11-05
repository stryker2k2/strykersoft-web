FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY . .
# CMD ["flask", "run", "-h", "0.0.0.0"]
# CMD python3 flask/run.py

# docker build -t flask .
