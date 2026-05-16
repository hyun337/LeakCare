import BASE_URL, { COMMON_HEADERS } from './client';

export const uploadPhoto = async (file) => {
  const token = localStorage.getItem('accessToken');
  
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/faces/register`, {
    method: 'POST',
    headers: {
      ...COMMON_HEADERS, 
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
    body: formData,
  });

  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};

export const getFaceStatus = async () => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/faces/status`, {
    headers: {
      ...COMMON_HEADERS,
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};

export const deletePhoto = async (photoIndex) => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`${BASE_URL}/faces/register/${photoIndex}`, {
    method: 'DELETE',
    headers: {
      ...COMMON_HEADERS,
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });

  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};
