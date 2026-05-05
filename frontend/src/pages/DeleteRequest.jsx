//삭제 요청서 
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getDeleteRequest } from "../api/reportApi";
import "../styles/DeleteRequest.css";

export default function DeleteRequest() {
  const { reportId } = useParams();

  const [report, setReport] = useState(null);
  const [mailKo, setMailKo] = useState("");
  const [mailEn, setMailEn] = useState("");
  const [activeTab, setActiveTab] = useState("ko");
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError("");

        const res = await getDeleteRequest(reportId);
        if (res.ok) {
          setReport(res.data.report);
          setMailKo(res.data.mail_ko || "");
          setMailEn(res.data.mail_en || "");
        } else {
          setError("삭제 요청서를 불러오는데 실패했습니다. 다시 시도해주세요.");
        }
      } catch (err) {
        console.error("삭제 요청서 로딩 실패:", err);
        setError("삭제 요청서를 불러오는데 실패했습니다. 다시 시도해주세요.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [reportId]);

  const handleCopy = () => {
    const text = activeTab === "ko" ? mailKo : mailEn;
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleMailto = () => {
    const subject = encodeURIComponent("불법 유출 콘텐츠 삭제 요청 / Content Removal Request");
    const body = encodeURIComponent(activeTab === "ko" ? mailKo : mailEn);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  const formattedDate = report?.collected_at
    ? new Date(report.collected_at).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })
    : "-";

  if (loading) {
    return (
      <div className="dr-loading">
        <div className="dr-spinner" />
        <p>삭제 요청 메일을 생성하고 있습니다...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dr-loading">
        <p style={{ color: "red" }}>{error}</p>
      </div>
    );
  }

  if (!report) return <div className="dr-loading"><p>데이터가 없습니다.</p></div>;

  return (
    <div className="dr-page">
      <div className="dr-header">
        <h1 className="dr-title">삭제 요청서</h1>
        <p className="dr-subtitle">AI가 생성한 삭제 요청 메일입니다. 복사 후 직접 발송해주세요.</p>
      </div>

      <div className="dr-card">
        <p className="dr-card-label">탐지 요약</p>
        <div className="dr-meta-row">
          <div className="dr-meta-item">
            <span className="dr-meta-key">판정 결과</span>
            <span className="dr-badge dr-badge--danger">
              ● {report.is_leaked ? "유출 확인" : "미확인"}
            </span>
          </div>
          <div className="dr-meta-item">
            <span className="dr-meta-key">게시 URL</span>
            <span className="dr-meta-val dr-meta-val--link">{report.target_url || report.url}</span>
          </div>
          <div className="dr-meta-item">
            <span className="dr-meta-key">유사도</span>
            <span className="dr-meta-val">{report.score}%</span>
          </div>
          <div className="dr-meta-item">
            <span className="dr-meta-key">서버 국가</span>
            <span className="dr-meta-val">{report.country}</span>
          </div>
          <div className="dr-meta-item">
            <span className="dr-meta-key">수집 일시</span>
            <span className="dr-meta-val">{formattedDate}</span>
          </div>
        </div>
      </div>

      <div className="dr-card">
        <div className="dr-tabs">
          <button
            className={`dr-tab ${activeTab === "ko" ? "dr-tab--active" : ""}`}
            onClick={() => setActiveTab("ko")}
          >
            한국어
          </button>
          <button
            className={`dr-tab ${activeTab === "en" ? "dr-tab--active" : ""}`}
            onClick={() => setActiveTab("en")}
          >
            English
          </button>
        </div>

        <div className="dr-mail-box">
          <textarea
            className="dr-mail-text"
            value={activeTab === "ko" ? mailKo : mailEn}
            onChange={(e) =>
              activeTab === "ko"
                ? setMailKo(e.target.value)
                : setMailEn(e.target.value)
            }
            rows={16}
          />
        </div>

        <div className="dr-actions">
          <button className="dr-btn dr-btn--primary" onClick={handleCopy}>
            {copied ? "✓ 복사됨" : "클립보드에 복사"}
          </button>
          <button className="dr-btn dr-btn--secondary" onClick={handleMailto}>
            메일 앱으로 열기
          </button>
        </div>

        <div className="dr-note">
          직접 발송 기능은 제공되지 않습니다. 복사 후 이메일 클라이언트에서 발송해주세요.
          IP·위치 정보는 ip-api.com 기반으로 정확도에 한계가 있을 수 있습니다.
        </div>
      </div>
    </div>
  );
}
