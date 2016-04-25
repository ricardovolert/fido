FROM python:3.4-wheezy

RUN pip install slacker tornado
ADD ./server.py /tmp/server.py
EXPOSE 80
CMD ["python3", "/tmp/server.py"]
