import BASE_URL from './client';

// 작업 목록 조회
export const getDetectionHistory = async () => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`${BASE_URL}/detection/history`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { detail: text };
  }

  return { ok: response.ok, status: response.status, data };
};
