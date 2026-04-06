# Claude Status Bar

Claude Code용 커스텀 Status Line 플러그인입니다. 터미널 하단에 세션 정보를 실시간으로 표시합니다.

## 표시 정보

**출력 예시:**
```
📁 Test 🌿 master 🧠 MiniMax-M2.7
🧊 35% (48,000/200,000) [███░░░░░░░] In:45k Out:3k ⚡45t/s Avg:12t/s
🌐 5h: 174/4,500 (4%) 7d: 298/45,000 (1%) (R:2h5m/6d21h)
```

| 줄 | 내용 | 설명 |
|----|------|------|
| 1 | 📁 디렉토리 🌿 브랜치 🧠 모델 | 현재 작업 환경 |
| 2 | 🧊 컨텍스트 In/Out ⚡속도 | 토큰 사용량 + 생성 속도 |
| 3 | 🌐 API Rate Limit + 리셋시간 | Claude/MiniMax API 한도 |

## 주요 기능

- **토큰 카운트**: Input/Output 토큰 각각 표시 (천 단위 축약: 45k)
- **토큰 속도**: 현재 생성 속도 (⚡45t/s) + 세션 평균 (Avg:12t/s)
- **프로그레스 바**: 10칸 그래프로 사용률 시각화
- **Rate Limit 모니터링**: 5시간/7일 창 잔여량 및 리셋 시간
- **Git 정보**: 브랜치/스테이징 상태 (5초 캐싱)

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/install.sh | bash
```

## 업데이트

```bash
curl -fsSL https://raw.githubusercontent.com/PriuS2/ClaudeCode-StatusLine/main/update.sh | bash
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
echo '{"model":{"display_name":"MiniMax-M2.7"},"context_window":{"used_percentage":35,"context_window_size":200000,"current_usage":{"input_tokens":45000,"output_tokens":3000},"total_output_tokens":3000},"cost":{"total_cost_usd":0.00,"total_duration_ms":3600000,"total_api_duration_ms":250000},"workspace":{"current_dir":"/test"}}' | python3 statusline.py
```

## 참고사항

- `rate_limits` 필드는 Claude.ai 구독자(Pro/Max)만 사용 가능
- Git 정보는 5초마다 캐싱하여 성능 최적화
- 토큰 속도는 30초 캐싱 (속도 데이터가 없으면 `-- t/s`로 표시)

## 라이선스

MIT
