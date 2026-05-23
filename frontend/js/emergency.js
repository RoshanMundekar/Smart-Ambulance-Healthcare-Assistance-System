/**
 * Emergency booking and tracking logic
 */

let emergencyActive = false;
let currentEmergencyId = null;

async function triggerEmergency() {
  if (emergencyActive) {
    alert('Emergency request already active.');
    return;
  }

  if (!userLocation) {
    alert('⚠️ Location not detected. Please enable location access and try again.');
    detectLocation();
    return;
  }

  const btn = document.getElementById('emergency-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Dispatching...';
  btn.classList.add('opacity-75');

  try {
    const user = getCurrentUser();
    const payload = {
      latitude: userLocation.lat,
      longitude: userLocation.lng,
      emergency_type: 'other',
      symptoms: user?.medical_history || '',
    };

    const result = await apiPost('/emergency/request', payload);
    emergencyActive = true;
    currentEmergencyId = result.id;

    // Show status card
    const card = document.getElementById('emergency-status-card');
    card.classList.remove('hidden');
    document.getElementById('em-status-badge').textContent = result.status.replace('_', ' ').toUpperCase();
    document.getElementById('em-eta').textContent = result.eta_minutes ? `${result.eta_minutes} min` : 'Calculating...';
    document.getElementById('em-ai-rec').textContent = result.ai_specialist_recommendation
      ? `Recommended Specialist: ${result.ai_specialist_recommendation}`
      : 'AI analysis complete';

    btn.textContent = '🚑 Help is Coming';
    btn.classList.add('bg-green-100', 'text-green-700');
    btn.classList.remove('text-red-600');

    // Poll for updates
    pollEmergencyStatus(result.id);

  } catch (err) {
    alert('Emergency request failed: ' + err.message + '\n\nPlease call 108 directly!');
    btn.disabled = false;
    btn.textContent = '🆘 SOS EMERGENCY';
    btn.classList.remove('opacity-75');
  }
}

async function pollEmergencyStatus(emergencyId) {
  if (!emergencyId) return;
  const interval = setInterval(async () => {
    try {
      const data = await apiGet(`/emergency/${emergencyId}`);
      updateEmergencyUI(data);
      if (['completed', 'cancelled'].includes(data.status)) {
        clearInterval(interval);
        emergencyActive = false;
      }
    } catch {}
  }, 10000); // Poll every 10 seconds
}

function updateEmergencyUI(data) {
  const badge = document.getElementById('em-status-badge');
  const eta = document.getElementById('em-eta');

  if (badge) {
    badge.textContent = data.status.replace(/_/g, ' ').toUpperCase();
    const colorMap = {
      requested: 'bg-yellow-100 text-yellow-700',
      ambulance_assigned: 'bg-blue-100 text-blue-700',
      en_route: 'bg-purple-100 text-purple-700',
      at_scene: 'bg-orange-100 text-orange-700',
      transporting: 'bg-red-100 text-red-700',
      arrived: 'bg-green-100 text-green-700',
      completed: 'bg-green-200 text-green-800',
    };
    badge.className = `px-3 py-1 rounded-full text-sm font-semibold ${colorMap[data.status] || 'bg-gray-100 text-gray-700'}`;
  }
  if (eta && data.eta_minutes) {
    eta.textContent = `${data.eta_minutes} min`;
  }
  if (data.assigned_ambulance_id) {
    const ambEl = document.getElementById('em-ambulance');
    if (ambEl) ambEl.textContent = `AMB-#${data.assigned_ambulance_id}`;
  }
}
