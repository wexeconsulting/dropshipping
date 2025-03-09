
FROM python:3.9-slim
#RUN apt update && apt install -y python3-psycopg2 libpq-dev python3-dev
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENV NAME World
CMD ["streamlit", "run", "app.py"]