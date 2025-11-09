import express from 'express';
import { setRoutes } from './routes/index';
import { json, urlencoded } from 'body-parser';

const app = express();

// Middleware
app.use(json());
app.use(urlencoded({ extended: true }));

// Set up routes
setRoutes(app);

export default app;