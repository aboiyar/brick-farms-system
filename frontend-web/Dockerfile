FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package.json yarn.lock* package-lock.json* ./
RUN if [ -f yarn.lock ]; then \
      apk add --no-cache curl git; \
      npm install -g yarn; \
      yarn install --frozen-lockfile; \
    else \
      npm ci; \
    fi

# Copy sources and build
COPY . ./
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
