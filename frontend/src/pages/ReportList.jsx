import React from 'react';
import { useNavigate } from 'react-router-dom';

function ReportList() {
  const navigate = useNavigate();

  // 테스트용 데이터 API연결 예정
  const dummyReports = [
    { id: 1, url: 'https://example.com/site1', result: '유출 확인', date: '2026-03-25' },
    { id: 2, url: 'https://test-site.org/page', result: '미확인', date: '2026-03-26' },
  ];

  return (
    <div className="report-list-container" style={{ padding: '20px' }}>
      <h2>결과 보고서 목록</h2>
      <p>탐지 완료된 리스트를 확인하고 상세 보고서를 열람하세요.</p>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>ID</th>
            <th style={{ padding: '12px' }}>탐지 URL</th>
            <th style={{ padding: '12px' }}>판정 결과</th>
            <th style={{ padding: '12px' }}>생성일</th>
            <th style={{ padding: '12px' }}>상세 보기</th>
          </tr>
        </thead>
        <tbody>
          {dummyReports.map((report) => (
            <tr key={report.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '12px' }}>{report.id}</td>
              <td style={{ padding: '12px' }}>{report.url}</td>
              <td style={{ padding: '12px' }}>
                <span style={{ color: report.result === '유출 확인' ? 'red' : 'green' }}>
                  {report.result}
                </span>
              </td>
              <td style={{ padding: '12px' }}>{report.date}</td>
              <td style={{ padding: '12px' }}>
                <button onClick={() => navigate(`/reports/${report.id}`)}>확인</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ReportList;