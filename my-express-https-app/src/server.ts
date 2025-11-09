import express from 'express';
import https from 'https';
import fs from 'fs';
import { setRoutes } from './routes/index';

const app = express();
const PORT = process.env.PORT || 3000;

const options = {
  key: fs.readFileSync('certs/localhost.key'),
  cert: fs.readFileSync('certs/localhost.crt'),
};

setRoutes(app);

const server = https.createServer(options, app);

server.listen(PORT, () => {
  console.log(`HTTPS Server is running on https://localhost:${PORT}`);
});