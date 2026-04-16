/**
 * settings.js
 */

document.addEventListener('DOMContentLoaded', async () => {
  await loadConfiguration();
});

async function loadConfiguration() {
  try {
    const data = await apiFetch('/config');
    
    // Populate form
    document.getElementById('cfg-high-bias').value = data.thresholds?.high_bias || 30;
    document.getElementById('cfg-mid-bias').value = data.thresholds?.medium_bias || 15;
    
    document.getElementById('cfg-exp-mult').value = data.company_point_system?.experience_multiplier || 10;
    document.getElementById('cfg-gpa-mult').value = data.company_point_system?.gpa_multiplier || 20;
    document.getElementById('cfg-passing').value = data.company_point_system?.passing_score || 60;
    
    document.getElementById('cfg-age-penalty').value = data.demo?.age_bias_penalty || 20;
    document.getElementById('cfg-age-thresh').value = data.demo?.age_bias_threshold || 40;
    document.getElementById('cfg-name-penalty').value = data.demo?.name_bias_penalty || 30;
    
  } catch (err) {
    showResult('save-result', `Error loading config: ${err.message}`, true);
  }
}

async function saveConfiguration() {
  const btn = document.getElementById('save-btn');
  btn.textContent = 'Saving...';
  btn.disabled = true;
  
  const payload = {
    thresholds: {
      high_bias: parseFloat(document.getElementById('cfg-high-bias').value),
      medium_bias: parseFloat(document.getElementById('cfg-mid-bias').value),
    },
    company_point_system: {
      experience_multiplier: parseFloat(document.getElementById('cfg-exp-mult').value),
      gpa_multiplier: parseFloat(document.getElementById('cfg-gpa-mult').value),
      passing_score: parseFloat(document.getElementById('cfg-passing').value),
    },
    demo: {
      age_bias_penalty: parseFloat(document.getElementById('cfg-age-penalty').value),
      age_bias_threshold: parseFloat(document.getElementById('cfg-age-thresh').value),
      name_bias_penalty: parseFloat(document.getElementById('cfg-name-penalty').value),
    }
  };
  
  try {
    const res = await apiFetch('/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    showResult('save-result', res.message || 'Configuration successfully updated.');
  } catch (err) {
    showResult('save-result', `Error saving config: ${err.message}`, true);
  } finally {
    btn.textContent = 'Save Configuration';
    btn.disabled = false;
  }
}
