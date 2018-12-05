FROM python:3.6-alpine

WORKDIR /app

# Install dependencies for numpy
RUN apk add --no-cache \
    g++ openblas-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm -rf /root/.cache && rm requirements.txt

COPY events/ events/
COPY main.py .
CMD ["sh", "-c", "python3 main.py"]
