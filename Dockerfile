FROM rayproject/ray:2.40.0-py311

WORKDIR /home/ray/app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/app.py ./
COPY app/static ./static

# Lets Ray Serve resolve import_path "app:app" on head and worker pods
ENV PYTHONPATH=/home/ray/app
