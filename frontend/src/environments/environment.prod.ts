// DEPLOYMENT NOTE:
// - Docker Compose (default): nginx proxies /api → backend, so relative '/api' works fine.
// - Railway / Render (frontend + backend as SEPARATE services):
//     Replace '/api' below with your full backend URL, e.g.:
//     apiUrl: 'https://your-backend-name.railway.app/api'
//   You can also inject this at build time via an environment variable.
export const environment = {
  production: true,
  apiUrl: '/api',
};
