(function (global) {
  const defaults = {
    // API_BASE_URL: 'http://127.0.0.1:8001',
    
    API_BASE_URL: 'https://mycontrol-c4ajevh3adbqe7fk.westcentralus-01.azurewebsites.net',
    AUTH_BASE_URL: null,
  };

  const existing = global.APP_CONFIG || {};
  const resolvedApiBase = (existing.API_BASE_URL || existing.API_BASE || defaults.API_BASE_URL).replace(/\/$/, '');
  const resolvedAuthBase = (existing.AUTH_BASE_URL || existing.AUTH_BASE || existing.API_BASE_URL || resolvedApiBase || defaults.API_BASE_URL);

  const config = {
    API_BASE_URL: resolvedApiBase,
    AUTH_BASE_URL: resolvedAuthBase.replace(/\/$/, ''),
  };

  global.APP_CONFIG = config;
  global.API_BASE_URL = config.API_BASE_URL;
  global.AUTH_BASE_URL = config.AUTH_BASE_URL;

  global.buildApiUrl = function buildApiUrl(path) {
    if (!path) {
      return config.API_BASE_URL;
    }
    if (/^https?:/i.test(path)) {
      return path;
    }
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${config.API_BASE_URL}${normalizedPath}`;
  };

  global.buildAuthUrl = function buildAuthUrl(path) {
    if (!path) {
      return config.AUTH_BASE_URL;
    }
    if (/^https?:/i.test(path)) {
      return path;
    }
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${config.AUTH_BASE_URL}${normalizedPath}`;
  };
})(window);

