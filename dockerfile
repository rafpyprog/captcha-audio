FROM ubuntu:17.04

ENV app /captcha-audio

# Install system dependencies
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y sox
RUN apt-get install -y xvfb
RUN apt-get install -y unzip openjdk-8-jre-headless libxi6 libgconf-2-4
RUN apt-get install -y python3.6
RUN apt-get install -y wget
RUN curl -o /tmp/get-pip.py "https://bootstrap.pypa.io/get-pip.py"
RUN python3.6 /tmp/get-pip.py

# Install app python requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# Create app folder and copy source code
RUN mkdir $app
COPY *.py $app/


# Install Chromedriver
ENV CHROMEDRIVER_VERSION 2.33
ENV PATH $app:$PATH

RUN curl https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    --output /captcha-audio/chromedriver_linux64.zip \
    && unzip /captcha-audio/chromedriver_linux64.zip -d /captcha-audio \
    && rm /captcha-audio/chromedriver_linux64.zip


# Install Chrome.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update
RUN apt-get -y install google-chrome-stable


# Remove unwanted files
RUN apt-get remove -y curl unzip && apt-get autoremove -y

WORKDIR /captcha-audio
