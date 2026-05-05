import BASE_URL from './client';

export const getReports = async () => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/reports/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) return [];
  return response.json();
};

export const getFullReport = async (taskId) => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/detection/full-report/${taskId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};

export const getDeleteRequest = async (taskId) => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/detection/summary-report/${taskId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};
