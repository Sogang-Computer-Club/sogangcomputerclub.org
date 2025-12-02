FROM python:3.13
WORKDIR /code
RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./README.md /code/
RUN uv sync --frozen --no-cache
COPY ./app /code/app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]