/**
 * Authentication helpers
 */

function getCurrentUser() {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveAuth(token, refreshToken, user) {
  localStorage.setItem('access_token', token);
  localStorage.setItem('refresh_token', refreshToken);
  localStorage.setItem('user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

function logout() {
  clearAuth();
  window.location.href = 'login.html';
}

function requireAuth() {
  const token = localStorage.getItem('access_token');
  const user = getCurrentUser();
  if (!token || !user) {
    window.location.href = 'login.html';
    return null;
  }
  return user;
}

function redirectByRole(role) {
  const roleRoutes = {
    patient: 'dashboard.html',
    driver: 'driver.html',
    doctor: 'consultation.html',
    hospital_admin: 'hospital.html',
    system_admin: 'admin.html',
  };
  window.location.href = roleRoutes[role] || 'dashboard.html';
}

// ---- Login Form Handler ----
function switchTab(tab) {
  document.getElementById('form-login').classList.toggle('hidden', tab !== 'login');
  document.getElementById('form-register').classList.toggle('hidden', tab !== 'register');
  document.getElementById('tab-login').className = tab === 'login'
    ? 'flex-1 py-4 font-semibold text-red-600 border-b-2 border-red-600 transition'
    : 'flex-1 py-4 font-semibold text-gray-400 border-b-2 border-transparent hover:text-red-600 transition';
  document.getElementById('tab-register').className = tab === 'register'
    ? 'flex-1 py-4 font-semibold text-red-600 border-b-2 border-red-600 transition'
    : 'flex-1 py-4 font-semibold text-gray-400 border-b-2 border-transparent hover:text-red-600 transition';
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  const btn = document.getElementById('login-btn');
  errEl.classList.add('hidden');
  btn.disabled = true;

  try {
    const data = await apiPost('/auth/login', { email, password });
    saveAuth(data.access_token, data.refresh_token, data.user);
    redirectByRole(data.user.role);
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const errEl = document.getElementById('register-error');
  const sucEl = document.getElementById('register-success');
  errEl.classList.add('hidden');
  sucEl.classList.add('hidden');

  const payload = {
    full_name: document.getElementById('reg-name').value,
    age: parseInt(document.getElementById('reg-age').value) || null,
    phone: document.getElementById('reg-phone').value,
    email: document.getElementById('reg-email').value,
    password: document.getElementById('reg-password').value,
    blood_group: document.getElementById('reg-blood').value || null,
    medical_history: document.getElementById('reg-history').value || null,
    role: 'patient',
  };

  document.getElementById('reg-btn').disabled = true;
  try {
    await apiPost('/auth/register', payload);
    sucEl.textContent = '✅ Account created! Please login.';
    sucEl.classList.remove('hidden');
    setTimeout(() => switchTab('login'), 1500);
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    document.getElementById('reg-btn').disabled = false;
  }
}

// WebSocket connection for real-time notifications
let ws = null;

function initWebSocket(userId) {
  if (!userId || ws) return;
  const wsUrl = `ws://localhost:8000/api/emergency/ws/${userId}`;
  ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleWsMessage(msg);
    } catch {}
  };

  ws.onclose = () => {
    ws = null;
    setTimeout(() => initWebSocket(userId), 5000); // Reconnect
  };
}

function handleWsMessage(msg) {
  if (msg.type === 'notification') {
    showToast(msg.data.title, msg.data.message);
    updateNotifBadge();
  } else if (msg.type === 'emergency_update') {
    updateEmergencyCard(msg.data);
  } else if (msg.type === 'location_update') {
    // Update map if on driver/patient page
    if (typeof updateMapMarker === 'function') updateMapMarker(msg.data);
  }
}

function showToast(title, message) {
  const toast = document.createElement('div');
  toast.className = 'fixed bottom-4 right-4 bg-white border-l-4 border-red-500 shadow-xl rounded-xl p-4 z-50 max-w-sm animate-slide-in';
  toast.innerHTML = `<p class="font-bold text-gray-800">${title}</p><p class="text-sm text-gray-600 mt-1">${message}</p>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

function updateNotifBadge() {
  const badge = document.getElementById('notif-badge');
  if (badge) {
    badge.classList.remove('hidden');
    badge.textContent = parseInt(badge.textContent || '0') + 1;
  }
}

function updateEmergencyCard(data) {
  const card = document.getElementById('emergency-status-card');
  if (card) {
    card.classList.remove('hidden');
    if (data.status) document.getElementById('em-status-badge').textContent = data.status.replace('_', ' ');
    if (data.eta) document.getElementById('em-eta').textContent = `${data.eta} min`;
  }
}
