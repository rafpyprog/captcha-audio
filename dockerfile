FROM joyzoursky/python-chromedriver:3.6-xvfb

ENV app /captcha-audio

RUN apt-get install -y sox

# Install python package requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt \
    && rm requirements.txt

# Create app folder and copy source code
RUN mkdir $app
#COPY *.py $app/

WORKDIR $app

EXPOSE 8888
