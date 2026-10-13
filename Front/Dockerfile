# Frontend Angular 20 - Sistema de Gestión de Mapoteca UAS
# Node 22: LTS soportado por Angular 20.
FROM node:22-alpine

WORKDIR /app

# Dependencias primero (mejor cache de capas en rebuilds)
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 4200

# --host 0.0.0.0: obligatorio para que ng serve sea accesible fuera del contenedor
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
