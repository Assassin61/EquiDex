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
    
    document.getElementById('cfg-passing').value = data.company_point_system?.passing_score || 60;
    
    const multipliers = data.company_point_system?.multipliers || {};
    const container = document.getElementById('dynamic-multipliers');
    container.innerHTML = '';
    for (const [key, val] of Object.entries(multipliers)) {
        addMultiplierField(key, val);
    }
    
    document.getElementById('cfg-age-penalty').value = data.demo?.age_bias_penalty || 20;
    document.getElementById('cfg-age-thresh').value = data.demo?.age_bias_threshold || 40;
    document.getElementById('cfg-name-penalty').value = data.demo?.name_bias_penalty || 30;
    
  } catch (err) {
    showResult('save-result', `Error loading config: ${err.message}`, true);
  }
}

function addMultiplierField(key = '', val = '') {
  const container = document.getElementById('dynamic-multipliers');
  const idStr = Date.now().toString() + Math.random().toString().slice(2, 6);
  
  const div = document.createElement('div');
  div.className = 'form-group obj-row';
  div.id = 'mult-row-' + idStr;
  div.style.display = 'flex';
  div.style.gap = '0.5rem';
  
  div.innerHTML = `
    <input type="text" class="mult-key" placeholder="Attribute (e.g. experience)" value="${key}" style="flex:1" />
    <input type="number" class="mult-val" placeholder="Points" value="${val}" style="flex:1" />
    <button class="btn btn-ghost" style="color:var(--danger); padding: 0.5rem;" onclick="document.getElementById('mult-row-${idStr}').remove()">X</button>
  `;
  container.appendChild(div);
}

async function saveConfiguration() {
  const btn = document.getElementById('save-btn');
  btn.textContent = 'Saving...';
  btn.disabled = true;
  
  const multipliersObj = {};
  document.querySelectorAll('#dynamic-multipliers .obj-row').forEach(row => {
    const k = row.querySelector('.mult-key').value.trim();
    const v = parseFloat(row.querySelector('.mult-val').value) || 0;
    if (k) multipliersObj[k] = v;
  });

  const payload = {
    thresholds: {
      high_bias: parseFloat(document.getElementById('cfg-high-bias').value),
      medium_bias: parseFloat(document.getElementById('cfg-mid-bias').value),
    },
    company_point_system: {
      multipliers: multipliersObj,
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
