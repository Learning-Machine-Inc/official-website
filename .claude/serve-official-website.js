const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PORT) || 3001;
const TYPES = { '.css':'text/css', '.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript', '.mp4':'video/mp4', '.png':'image/png', '.svg':'image/svg+xml', '.woff2':'font/woff2' };
const clients = new Set();

fs.watch(ROOT, { recursive:true }, () => {
  for (const client of clients) client.write('data: reload\n\n');
});

http.createServer((request, response) => {
  if (request.url === '/__livereload') {
    response.writeHead(200, { 'Cache-Control':'no-cache', Connection:'keep-alive', 'Content-Type':'text/event-stream' });
    clients.add(response);
    return request.on('close', () => clients.delete(response));
  }
  const relative = decodeURIComponent(request.url.split('?')[0] || '/').replace(/^\/$/, '/index.html');
  const file = path.resolve(ROOT, `.${relative}`);
  if (!file.startsWith(ROOT)) return response.writeHead(403).end();
  fs.readFile(file, (error, data) => {
    if (error) return response.writeHead(404).end('not found');
    response.setHeader('Content-Type', TYPES[path.extname(file)] || 'application/octet-stream');
    // Local dev only: never let the browser cache anything here, so an edit always shows up on
    // the next reload without needing a manual cache-busting query bump or a hard refresh.
    response.setHeader('Cache-Control', 'no-store');
    response.end(path.extname(file) === '.html' ? data.toString().replace('</body>', '<script>new EventSource("/__livereload").onmessage=()=>location.reload()</script></body>') : data);
  });
}).listen(PORT, () => console.log(`official website live reload: http://127.0.0.1:${PORT}`));
