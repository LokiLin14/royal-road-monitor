FROM docker.io/library/python:3.13.5-slim-bookworm

EXPOSE 5000/tcp

WORKDIR /app/
COPY ./src ./pyproject.toml ./LICENSE /app/
RUN pip install .

CMD ["flask", "--app", "royal_road_monitor", "run", "--host", "0.0.0.0"]