/**
 * API Client for Smart Ambulance & Healthcare System
 * All HTTP requests to the FastAPI backend
 */

const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

function authHeaders() {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse(res) {
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }

  if (!res.ok) {
    const detail = typeof data === 'object' ? (data.detail || JSON.stringify(data)) : data;

    // ── Global session-expiry handler ────────────────────────────────────────
    // 401 = token expired or missing → clear session and redirect to login
    if (res.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      // Avoid redirect loops if we are already on the login page
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login?expired=1';
      }
      // Throw so the current call stack unwinds cleanly (intervals stop naturally)
      throw new Error('401: Session expired. Please log in again.');
    }
    // ────────────────────────────────────────────────────────────────────────

    // 403 and all other errors: throw with status prefix so callers can detect them
    throw new Error(`${res.status}: ${detail || res.statusText}`);
  }
  return data;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return handleResponse(res);
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function apiPut(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function apiPatch(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handleResponse(res);
}
