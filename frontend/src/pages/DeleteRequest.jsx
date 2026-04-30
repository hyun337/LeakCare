//삭제 요청서 
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
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

        // TODO: API 완성 시 아래 주석 해제
        // const res = await getDeleteRequest(reportId);
        // setReport(res.data.report);
        // setMailKo(res.data.mail_ko);
        // setMailEn(res.data.mail_en);

        // 더미데이터 (API 연동 전 임시)
        setReport({
          task_id: reportId,
          target_url: "https://example.com/site1",
          score: 94.5,
          collected_at: "2026-03-25T14:32:00Z",
          ip_address: "123.456.78.9",
          country: "South Korea",
          is_leaked: true,
        });
        setMailKo(`수신: 운영자 귀중\n\n안녕하세요.\n\n본 메일은 귀하의 플랫폼에 게시된 콘텐츠의 삭제를 요청드리기 위해 작성하였습니다.\n\n해당 콘텐츠는 저의 동의 없이 게시된 영상/이미지로, 개인정보 보호법 및 관련 법률에 위반되는 불법 유출물에 해당합니다.\n\n■ 게시 URL: https://example.com/site1\n■ 탐지 일시: 2026-03-25 14:32 KST\n■ 유사도: 94.5%\n■ 서버 국가: South Korea\n\n즉각적인 삭제 조치와 함께 삭제 완료 시 회신 부탁드립니다.\n이에 응하지 않을 경우 법적 조치를 취할 수 있음을 알려드립니다.\n\n감사합니다.`);
        setMailEn(`Dear Administrator,\n\nI am writing to request the immediate removal of content posted on your platform without my consent.\n\nThe content in question constitutes illegally distributed material in violation of applicable privacy laws and regulations.\n\n■ URL: https://example.com/site1\n■ Detected at: 2026-03-25 14:32 KST\n■ Similarity score: 94.5%\n■ Server country: South Korea\n\nI kindly request that you remove this content immediately and notify me once the removal has been completed.\nPlease be advised that failure to comply may result in legal action.\n\nThank you.`);

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
            <span className="dr-meta-val dr-meta-val--link">{report.target_url}</span>
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
