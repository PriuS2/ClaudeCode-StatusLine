# Claude Status Bar

Claude Code용 커스텀 Status Line 플러그인입니다. 터미널 하단에 세션 정보를 실시간으로 표시합니다.

## 표시 정보

**출력 예시:**
```
📁 Test 🌿 master 🧠 MiniMax-M2.7
🧊 35% (48,000/200,000) [███░░░░░░░] In:45k Out:3k ⚡ 152t/s
🌐 5h: 174/4,500 (4%) 7d: 298/45,000 (1%) (R:2h5m/6d21h)
```

| 줄 | 내용 | 설명 |
|----|------|------|
| 1 | 📁 디렉토리 🌿 브랜치 🧠 모델 | 현재 작업 환경 |
| 2 | 🧊 컨텍스트 In/Out ⚡ 속도 | 토큰 사용량 및 응답 속도 |
| 3 | 🌐 API Rate Limit + 리셋시간 | Claude/MiniMax API 한도 |

## 주요 기능

- **실시간 응답 속도**: `⚡ 152t/s` - 마지막 API 응답 기반 속도 (모델 응답 종료 후에도 마지막 값 유지)
- **토큰 카운트**: Input/Output 토큰 각각 표시 (천 단위 축약: 45k)
- **프로그레스 바**: 10칸 그래프로 사용률 시각화
- **Rate Limit 모니터링**: 5시간/7일 창 잔여량 및 리셋 시간
- **Git 정보**: 브랜치/스테이징 상태 (5초 캐싱)

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/install.sh | bash
```

## 업데이트

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/install.sh | bash
```

## 제거

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/uninstall.sh | bash
```

## 요구사항

- Python 3
- Claude Code CLI

## 수동 테스트

```bash
echo '{"model":{"display_name":"MiniMax-M2.7"},"context_window":{"used_percentage":35,"context_window_size":200000,"current_usage":{"input_tokens":45000,"output_tokens":3000}},"cost":{"total_cost_usd":0.00,"total_duration_ms":3600000,"total_api_duration_ms":700000},"workspace":{"current_dir":"/test"}}' | python3 statusline.py
```

## 응답 속도 참고

| 모델 | 일반적인 속도 범위 |
|------|------------------|
| Claude Sonnet 4 | 40-80 t/s |
| Claude Opus 4 | 30-60 t/s |
| MiniMax-M2.7 | 100-300 t/s |

## 참고사항

- `rate_limits` 필드는 Claude.ai 구독자(Pro/Max)만 사용 가능
- 속도 측정은 `total_api_duration_ms` 기반 ( wall-clock 시간 아님)
- Git 정보는 5초마다 캐싱하여 성능 최적화

## 라이선스

MIT
