FROM python:3.6.8 AS builder
WORKDIR /usr/src
RUN python -m venv venv
COPY . app
RUN ./venv/bin/pip install pip --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple \
&& ./venv/bin/pip install --no-cache-dir -r ./app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

FROM python:3.6.8-slim AS release
COPY --from=builder /usr/src /usr/src
WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/src:/usr/src/app/holiday-cn"
ENTRYPOINT ["/usr/src/venv/bin/gunicorn", "main:app", "-c", "gunicorn.conf.py"]
CMD []