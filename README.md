# Release Note Auto

Wellysis 릴리즈 노트 자동화 도구. SDK / App / Firmware 등 모든 제품군의 Release Notes (PDF + Screenshot)를 Git 태그와 커밋 메시지로 자동 생성하고 Slack으로 알림을 보냅니다.

## 지원 제품군

| 타입 | 예시 | 태그 컨벤션 |
|------|------|------------|
| SDK | Wellysis iOS/Android SDK | `ios-sdk-2.1.6` / `android-sdk-2.1.6` |
| App | S-patch Ex iOS/Android | `spatchex-ios-1.6.8` / `spatchex-android-1.6.8` |
| FW  | Firmware | `fw-2.4.6` |

## 사용법 (Method B — 권장)

```bash
# 1. config 편집
vi config/release_config.yaml

# 2. commit + tag + push → GitHub Actions 자동 실행
git add config/release_config.yaml
git commit -m "release: spatchex-ios-1.6.8"
git tag spatchex-ios-1.6.8
git push origin main --tags
```

## config 핵심 필드

```yaml
product_type: "app"        # sdk | app | fw
product_name: "S-patch Ex" # PDF 헤더에 표시될 이름
tag:  "spatchex-ios-1.6.8" # 비우면 최신 태그 자동 감지
date: "March 28, 2026"     # 비우면 오늘 날짜

platform: "iOS"            # iOS | Android | (FW는 비워도 됨)
version:  "1.6.8"

new_functionalities:
  - "새 기능 설명"

enhancements:
  - "개선 사항"

previous_versions:
  - version: "v1.6.7"
    description: "이전 버전 요약"
```

## Slack 알림

GitHub Actions Secret에 `SLACK_WEBHOOK_URL` 등록 → 태그 push 시 자동 발송.

로컬 테스트: config에 `enabled: true` + `webhook_url` 직접 입력.

## 로컬 실행

```bash
pip install -r requirements.txt
python main.py
```

출력:
- `output/pdf/*.pdf`
- `output/screenshot/*.png`

## GitHub Actions

`.github/workflows/release-notes.yml` — 태그 push 시 자동 실행, Artifacts 90일 보관.
