import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/login.css';
import { loginUser } from '../api/userApi';

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert('이메일과 비밀번호를 모두 입력해주세요.');
      return;
    }

    try {
      setLoading(true);

      const result = await loginUser({ email, password });

      console.log('로그인 상태코드:', result.status);
      console.log('로그인 응답내용:', result.data);

      if (!result.ok) {
        let errorMessage = '로그인에 실패했습니다.';

        if (typeof result.data?.detail === 'string') {
          errorMessage = result.data.detail;
        } else if (Array.isArray(result.data?.detail)) {
          errorMessage = result.data.detail.map((err) => err.msg).join('\n');
        } else if (typeof result.data?.message === 'string') {
          errorMessage = result.data.message;
        }

        alert(errorMessage);
        return;
      }

      //  실제 토큰 및 유저 정보 저장
      localStorage.setItem('accessToken', result.data.access_token);
      localStorage.setItem('userId', result.data.user_id);
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', result.data.name);

      console.log('로그인 성공 → 대시보드 이동');
      navigate('/dashboard', { replace: true });

    } catch (error) {
      console.error('로그인 서버 연결 오류:', error);
      alert('서버에 연결할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="common-card login-box">
        <h1>📸 LeakCare</h1>
        <p className="login-subtitle">불법 촬영 유출물 탐지 플랫폼</p>

        <form className="login-form" onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="이메일 주소"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <div style={{ textAlign: 'right', marginBottom: '15px' }}>
            <Link
              to="/forgot-password"
              style={{
                fontSize: '0.8rem',
                color: 'gray',
                textDecoration: 'none',
              }}
            >
              비밀번호를 잊으셨나요?
            </Link>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div style={{ marginTop: '20px', fontSize: '0.85rem' }}>
          <span>계정이 없으신가요?</span>
          <Link
            to="/register"
            style={{
              marginLeft: '8px',
              textDecoration: 'none',
              fontWeight: 'bold',
            }}
          >
            회원가입
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
