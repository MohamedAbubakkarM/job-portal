# SvelteKit image shared by site/ and recruiter/. Build context is the app dir:
#   docker build -f frontend.Dockerfile site
#   docker build -f frontend.Dockerfile recruiter

FROM node:22-alpine AS build
WORKDIR /app
RUN npm install -g pnpm@10.12.1
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN pnpm install --frozen-lockfile
COPY . .

# $env/static/public values are baked into the bundle at build time, so each
# environment's URLs are passed as build args. Unused ones stay empty.
ARG PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
ARG PUBLIC_SITE_URL=http://localhost:5173
ARG PUBLIC_RECRUITER_URL=http://localhost:5174
ARG PUBLIC_JOBSEEKER_URL=http://localhost:5173
ENV PUBLIC_API_BASE_URL=$PUBLIC_API_BASE_URL \
    PUBLIC_SITE_URL=$PUBLIC_SITE_URL \
    PUBLIC_RECRUITER_URL=$PUBLIC_RECRUITER_URL \
    PUBLIC_JOBSEEKER_URL=$PUBLIC_JOBSEEKER_URL
RUN pnpm build && pnpm prune --prod

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3000
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/build ./build
USER node
EXPOSE 3000
# ORIGIN (the public URL, e.g. https://peeljobs-site.onrender.com) must be set
# at run time; SvelteKit uses it for its CSRF check on form posts.
CMD ["node", "build"]
