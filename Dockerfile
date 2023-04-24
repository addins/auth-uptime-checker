FROM python:3.12.0a7-alpine
RUN pip install requests python-dotenv
RUN adduser -D python
RUN mkdir /home/python/app/ && chown -R python:python /home/python/app
WORKDIR /home/python/app
USER python
EXPOSE 8080
ADD main.py .
ADD .env .
ENTRYPOINT [ "python", "./main.py"]