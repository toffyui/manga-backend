FROM public.ecr.aws/lambda/python:3.11

RUN yum update -y \
    && yum install -y \
    gcc-c++ \
    cmake \
    git \
    libglvnd-glx \
    libSM \
    libXrender \
    libXext \
    libXinerama \
    opencv \
    opencv-devel \
    python3-devel \
    && yum clean all

# Copy images to temp folder
COPY images/ ${LAMBDA_TASK_ROOT}/images/

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
