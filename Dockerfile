FROM python:3.10-alpine

WORKDIR /app
COPY . .

RUN cd setup

RUN pwd
RUN ls

RUN chmod +x build.sh
RUN ./build.sh

RUN pwd
RUN ls

RUN chmod +x setup.sh
RUN ./setup.sh install

EXPOSE 7500

CMD ["oniond", "start"]