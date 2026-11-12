# STEP 1: builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# STEP 2: runtime
FROM nginx:alpine AS runtime
COPY --from=builder /app/dist /usr/share/nginx/html
COPY templates/default.conf.template /etc/nginx/templates/default.conf.template
ENV APP_UPSTREAM=backend:5000
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
