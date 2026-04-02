import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/login.css';
import { registerUser } from '../api/userApi';

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();

    if (!agreed) {
      alert('개인정보 수집 및 이용에 동의해주세요.');
      return;
    }

    if (!name || !email || !password) {
      alert('모든 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);

      const result = await registerUser({
        name,
        email,
        password,
      });

      console.log('상태코드:', result.status);
      console.log('응답내용:', result.data);

      if (result.ok) {
        console.log('회원가입 성공:', result.data);
        alert('회원가입이 완료되었습니다. 로그인 페이지로 이동합니다.');
        navigate('/login');
      } else {
        console.error('회원가입 실패:', result.data);

        let errorMessage = `회원가입 실패 (${result.status})`;

        if (typeof result.data.detail === 'string') {
          if (result.data.detail.includes('value is not a valid email address')) {
            errorMessage = '올바른 이메일 형식으로 입력해주세요. 예: example@test.com';
          } else {
            errorMessage = result.data.detail;
          }
        } else if (Array.isArray(result.data.detail)) {
          const messages = result.data.detail.map((err) => {
            if (err.msg?.includes('value is not a valid email address')) {
              return '올바른 이메일 형식으로 입력해주세요. 예: example@test.com';
            }
            return err.msg;
          });

          errorMessage = messages.join('\n');
        } else if (typeof result.data.message === 'string') {
          errorMessage = result.data.message;
        } else if (typeof result.data === 'string') {
          errorMessage = result.data;
        }

        alert(errorMessage);
      }
    } catch (error) {
      console.error('서버 연결 오류:', error);
      alert('서버에 연결할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="common-card login-box">
        <h1>📸 LeakCare</h1>
        <p className="login-subtitle">내 계정 만들기</p>

        <form className="login-form" onSubmit={handleRegister}>
          <input
            type="text"
            placeholder="이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <input
            type="email"
            placeholder="이메일 주소 (예: example@test.com)"
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

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              textAlign: 'left',
              marginTop: '10px',
              padding: '0 5px',
            }}
          >
            <input
              type="checkbox"
              id="agree"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              style={{ width: '18px', height: '18px', cursor: 'pointer' }}
            />
            <label
              htmlFor="agree"
              style={{
                fontSize: '0.85rem',
                color: 'var(--text-sub)',
                cursor: 'pointer',
              }}
            >
              개인정보 수집 및 이용에 동의합니다.
            </label>
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ marginTop: '10px' }}
            disabled={loading}
          >
            {loading ? '가입 중...' : '가입하기'}
          </button>
        </form>

        <div
          style={{
            marginTop: '25px',
            fontSize: '0.85rem',
            color: 'var(--text-sub)',
          }}
        >
          <span>이미 계정이 있으신가요?</span>
          <Link
            to="/login"
            style={{
              color: 'var(--primary)',
              marginLeft: '8px',
              textDecoration: 'none',
              fontWeight: 'bold',
            }}
          >
            로그인
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;