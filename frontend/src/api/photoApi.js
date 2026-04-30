import BASE_URL from './client';

export const uploadPhoto = async (file) => {
  const token = localStorage.getItem('accessToken');
  
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/faces/register`, {
    method: 'POST',
    headers: {
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
