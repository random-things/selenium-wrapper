FROM python:3.11
WORKDIR /src

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get -y install apt-utils apt-transport-https curl \
    && apt-get install -y google-chrome-stable \
    && apt-get install -yqq unzip \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && apt -y upgrade \
    && pip install --upgrade pip \
    && pip install poetry
COPY pyproject.toml ./
RUN poetry install --no-root
ENV DISPLAY=:0

COPY . .

CMD ["poetry", "run", "pytest"]
