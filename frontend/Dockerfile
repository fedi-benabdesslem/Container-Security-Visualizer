# Build stage
FROM node:20-slim as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Final stage
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
# Copy standard nginx config for SPA if needed
RUN echo "server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files \$uri \$uri/ /index.html; \
    } \
    }" > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
