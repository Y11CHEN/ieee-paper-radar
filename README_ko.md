# IEEE Paper Radar

IEEE Xplore에서 매주 최신 논문을 자동으로 수집하고, AI를 통해 개인 연구 방향에 맞게 순위를 매겨 큐레이션된 다이제스트를 이메일로 전송합니다.

[English](README.md) | [中文](README_zh.md)

## 기능 흐름

1. **수집** IEEE Xplore에서 지정된 저널/학회의 최신 논문 수집 (TPEL, TIE, ECCE, APEC)
2. **보강** Semantic Scholar에서 각 논문의 인용 수 조회
3. **요약** Gemini AI를 통해 각 논문의 기여를 2–3문장으로 요약
4. **추천** 연구 프로필과 대조하여 3단계로 분류 (강력 추천 / 읽을 가치 있음 / 건너뜀)
5. **분석** 최근 2년간 문헌의 연구 트렌드 분석
6. **발송** 포맷된 HTML 이메일을 받은 편지함으로 전송

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 연구 방향 설정

`config.py` 상단의 **사용자 설정** 섹션을 편집합니다:

```python
# 수신자
RECIPIENT_EMAILS = ["your@gmail.com"]

# 검색어: 필수 키워드 전체 포함 + 컨텍스트 키워드 하나 이상 포함
KEYWORDS_REQUIRED = ["switched capacitor"]
KEYWORDS_CONTEXT  = ["data center", "48V bus", "rack power", "server rack"]

# 모니터링할 IEEE 저널/학회
VENUES = {
    "TPEL": "IEEE Transactions on Power Electronics",
    ...
}

# 연구 프로필 — AI가 논문 관련성을 판단하는 데 사용
RESEARCH_PROFILE = """
연구 주제: ...
주요 관심사: ...
"""
```

### 3. 비밀키 설정

`.env.example`을 `.env`로 복사하고 내용을 입력합니다:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=AIza...          # aistudio.google.com/apikey (무료)
IEEE_XPLORE_API_KEY=...         # developer.ieee.org (무료)
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=xxxx-xxxx-xxxx  # Gmail 앱 비밀번호 (계정 비밀번호 아님)
```

> **Gmail 앱 비밀번호**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)에서 생성하세요.

## 사용 방법

```bash
# 최초 1회: 과거 2년치 논문 초기화 (이메일 미발송)
python main.py --init

# 매주 실행: 수집 → 보강 → 요약 → 추천 → 이메일 발송
python main.py
```

### Windows 작업 스케줄러 자동화

프로젝트에 포함된 `run_weekly.bat`을 Windows 작업 스케줄러에 등록하면 매주 자동으로 실행됩니다.

## 이메일 형식

```
[IEEE Paper Radar] 2026-W22 | 논문 5편

📚 이번 주 추천
  ── 강력 추천 ──────────────────────────
  ⭐⭐ A Soft-Switching Multiresonant...  (TPEL)
  이유: RSCC 토폴로지 유도 방법론을 직접적으로 발전시킴...

  ── 읽을 가치 있음 ─────────────────────
  ⭐ Flying Capacitor Multilevel...  (ECCE)

── 전체 신규 논문 (5편) ────────────────
  [1] ⭐⭐ 제목 — TPEL · 2026 · 인용 수: 3
      기여: ...

── 연구 트렌드 분석 ────────────────────
  발전 서사: ...
  방향 1: ...
```

## 기술 스택

| 구성 요소 | 기술 |
|----------|------|
| 논문 소스 | IEEE Xplore API |
| 인용 데이터 | Semantic Scholar API |
| AI 분석 | Google Gemini 2.5 Pro |
| 데이터베이스 | SQLite |
| 이메일 발송 | SMTP (Gmail) |
| 개발 언어 | Python 3.12+ |

## 테스트

```bash
python -m pytest tests/ -v
```

모든 외부 API는 mock 처리되어 테스트 중 실제 API 호출이 발생하지 않습니다.
