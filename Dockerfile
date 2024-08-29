FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements/requirements.txt

EXPOSE 8000
EXPOSE 8501

CMD uvicorn src.main:app --host 0.0.0.0 --port 8000 & streamlit run src/interface.py --server.port 8501
