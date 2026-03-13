FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* bun.lockb* ./

RUN \
  if [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable && pnpm install --frozen-lockfile; \
  elif [ -f bun.lockb ]; then bun install --frozen-lockfile; \
  else npm install; \
  fi

COPY . .

RUN npm run build

# ---- Production image (static files via nginx) ----
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

