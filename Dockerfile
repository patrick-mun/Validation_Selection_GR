FROM continuumio/miniconda3:latest

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# WHY: copied first to cache the environment layer. The editable install is
# executed after COPY . . because it needs the full source tree.
COPY environment.yml requirements.txt pyproject.toml ./
RUN conda env create -f environment.yml && conda clean -afy

COPY . .
RUN conda run --no-capture-output -n genorun-validation python -m pip install -e .

EXPOSE 8000

CMD ["conda", "run", "--no-capture-output", "-n", "genorun-validation", "bash", "-lc", "alembic upgrade head && gunicorn web.wsgi:app --bind 0.0.0.0:8000 --workers 2"]
