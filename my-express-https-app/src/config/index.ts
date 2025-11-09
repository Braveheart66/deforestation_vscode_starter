import dotenv from 'dotenv';

dotenv.config();

const config = {
  port: process.env.PORT || 3000,
  env: process.env.NODE_ENV || 'development',
  https: {
    key: process.env.HTTPS_KEY || 'certs/localhost.key',
    cert: process.env.HTTPS_CERT || 'certs/localhost.crt',
  },
};

export default config;