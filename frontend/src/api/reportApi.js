import BASE_URL from './client';

// 보고서 목록
export const getReports = async () => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/reports/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};

// 보고서 상세
export const getFullReport = async (taskId) => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/reports/${taskId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};

// 삭제 요청서 텍스트
export const getRemovalText = async (taskId) => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/reports/${taskId}/removal-text`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};
