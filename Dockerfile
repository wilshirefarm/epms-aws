FROM python:3.8-alpine
WORKDIR /app
COPY . /app
COPY requirements.txt /app
COPY db /app/db
COPY static /app/static
COPY templates /app/templates
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]