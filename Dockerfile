FROM public.ecr.aws/lambda/python:3.7
RUN pip install opencv-python
RUN pip install numpy
COPY app.py /var/task/
COPY images/ /var/task/images/
CMD [ "app.handler" ]
