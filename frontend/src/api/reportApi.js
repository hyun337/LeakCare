import BASE_URL from './client';

export const getReports = async () => {
  const token = localStorage.getItem('accessToken');
  const response = await fetch(`${BASE_URL}/reports/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error('보고서 목록 조회 실패');
  return response.json();
};
