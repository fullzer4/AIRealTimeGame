FROM node:23 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:23

WORKDIR /app

COPY --from=builder /app/out ./out

EXPOSE 3000

CMD ["npx", "serve@latest", "out"]
