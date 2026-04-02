import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function Result() {
  const { id } = useParams(); // URL에서 ID 추출
  const navigate = useNavigate();

  return (
    <div className="report-detail-container" style={{ padding: '20px' }}>
      <button onClick={() => navigate('/reports')}>← 목록으로 돌아가기</button>
      <h2 style={{ marginTop: '20px' }}>📄 보고서 상세 (ID: {id})</h2>
      
      <div style={{ background: 'white', padding: '20px', borderRadius: '8px', marginTop: '20px', border: '1px solid #ddd' }}>
        <h3>탐지 결과: <span style={{ color: 'red' }}>유출 확인</span></h3>
        <p><strong>유사도 점수:</strong> 94.5%</p>
        <p><strong>서버 IP:</strong> 123.456.78.9 (South Korea)</p>
        
        <div style={{ marginTop: '20px', border: '1px dashed #ccc', height: '200px', display: 'flex', alignItems: 'center', justifySelf: 'center' }}>
          <p>[탐지 스크린샷 영역]</p>
        </div>

        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
          <button style={{ padding: '10px 20px', cursor: 'pointer' }}>PDF 다운로드</button>
          <button style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#4f46e5', color: 'white', border: 'none', borderRadius: '4px' }}>
            삭제 요청서(LLM) 확인
          </button>
        </div>
      </div>
    </div>
  );
}

export default Result;