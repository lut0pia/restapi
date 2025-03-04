# syntax=docker/dockerfile:1

FROM python:3.9-alpine AS builder
RUN apk update && apk add cmake make g++

FROM builder AS robin
COPY ./program/robin /robin
RUN cmake -S /robin/cli /robin/cli/bld -DCMAKE_BUILD_TYPE=Release
RUN cmake --build /robin/cli/bld --config Release

FROM builder AS steve
COPY ./program/steve /steve
RUN cmake -S /steve /steve/bld -DCMAKE_BUILD_TYPE=Release
RUN cmake --build /steve/bld --config Release
RUN cmake --install /steve/bld --config Release

FROM python:3.9-alpine AS runtime
WORKDIR /app
EXPOSE 80/tcp
RUN apk update && apk add ffmpeg
RUN pip install --no-cache-dir --upgrade fastapi[standard]
COPY ./app /app
COPY --from=robin /robin /app/program/robin
COPY --from=steve /usr/local/bin/steve /usr/local/bin/steve
COPY --from=steve /usr/local/steve /usr/local/steve
CMD ["fastapi", "run", "main.py", "--port", "80"]
