FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système et compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    make \
    curl \
    librsvg2-bin \
    postgresql-client \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libffi-dev \
    libssl-dev \
    libyaml-dev \
    libzip-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Dossiers de travail
WORKDIR /opt/odoo

# Dépendances Python Odoo
COPY odoo/odoo-19.0/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir psycopg2-binary passlib

# Copie des sources de l'application (pour Render.com et la production autonome)
COPY odoo/odoo-19.0 /opt/odoo
COPY custom_addons /mnt/custom-addons
COPY oca /mnt/oca
COPY config /etc/odoo

# Configuration de l'Entrypoint et permissions
COPY docker/entrypoint.sh /docker/entrypoint.sh
RUN chmod +x /docker/entrypoint.sh && \
    chmod +x /opt/odoo/odoo-bin && \
    mkdir -p /var/lib/odoo && \
    chmod -R 777 /var/lib/odoo

EXPOSE 8069 10000

ENTRYPOINT ["/docker/entrypoint.sh"]
