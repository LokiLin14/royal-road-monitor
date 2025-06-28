FROM docker.io/library/python:3.13.5-bookworm

EXPOSE 5000/tcp

WORKDIR /app/
COPY ./src ./pyproject.toml ./LICENSE /app/
RUN pip install .

CMD ["flask", "--app", "new_in_rising_stars", "run", "--host", "0.0.0.0"]