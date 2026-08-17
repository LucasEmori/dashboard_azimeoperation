# Stage 1: build React frontend
FROM node:20-slim AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.js tailwind.config.js postcss.config.js ./
COPY src ./src
COPY public ./public
RUN npm run build

# Stage 2: serve
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Python deps p/ pipeline (BQ) quando rodar no container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY src/*.py ./src/
COPY --from=build /web/dist ./dist
# output/ entra via COPY abaixo se existir; Railway fallback dist/data.json
COPY output/ ./output/

EXPOSE 8501
ENV PORT=8501

ENTRYPOINT ["sh", "-c", "python app.py"]