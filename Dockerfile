FROM python:3.6

RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENV FLASK_APP=streaming.py
EXPOSE 8000
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "8000"]
