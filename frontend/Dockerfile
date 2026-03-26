# Frontend Dockerfile - SvelteKit 애플리케이션
# 멀티 스테이지 빌드: 빌드 도구는 최종 이미지에 포함되지 않아 이미지 크기 감소

# 빌드 스테이지 - 개발 의존성 포함
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 스테이지 - 런타임만 포함
FROM node:20-alpine AS production

# 보안: root가 아닌 전용 사용자로 실행
# Alpine의 기본 node 사용자(uid 1000) 활용
RUN addgroup -S appgroup && \
    adduser -S -G appgroup appuser

WORKDIR /app

# 프로덕션 의존성만 설치 (devDependencies 제외)
COPY --chown=appuser:appgroup package*.json ./
RUN npm ci --omit dev

# 빌드된 애플리케이션 복사 (소스 코드 미포함)
COPY --chown=appuser:appgroup --from=build /app/build ./build

# 비루트 사용자로 전환
USER appuser

EXPOSE 3000
ENV HOST=0.0.0.0
ENV PORT=3000

# 헬스 체크 - Alpine에는 curl 없으므로 wget 사용
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "build"]
