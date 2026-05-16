import BASE_URL, { COMMON_HEADERS } from './client';

// 회원가입
export const registerUser = async ({ name, email, password }) => {
  const response = await fetch(`${BASE_URL}/users/register`, {
    method: 'POST',
    headers: {
      ...COMMON_HEADERS, 
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      name,
      email,
      password,
    }),
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

// 로그인
export const loginUser = async ({ email, password }) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  formData.append('grant_type', 'password');

  const response = await fetch(`${BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
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

// 회원 탈퇴
export const deleteUser = async () => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`${BASE_URL}/users/me`, {  // ← /users/${userId} 에서 /users/me 로 수정
    method: 'DELETE',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  return { ok: response.ok, status: response.status };
};

// 비밀번호 변경
export const changePassword = async ({ currentPassword, newPassword }) => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(`${BASE_URL}/users/change-pw`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  return { ok: response.ok, status: response.status, data };
};
