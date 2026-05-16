import BASE_URL, { COMMON_HEADERS } from './client';

// 탐지 요청 생성
export const submitDetectRequest = async ({ url }) => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`${BASE_URL}/detection/analyze`, {
    method: 'POST',
    headers: {
      ...COMMON_HEADERS, 
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ url }),
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
