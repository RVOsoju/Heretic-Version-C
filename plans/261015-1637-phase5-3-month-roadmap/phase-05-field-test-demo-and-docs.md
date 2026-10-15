---
phase: 5
title: "Field test + stress + demo E2E 10 phút + tài liệu đồ án (M5)"
status: pending
priority: P1
effort: "4w"
dependencies: [phase-04]
---

# Phase 5: Field test + stress + demo E2E + tài liệu (M5)

## Overview

W9–W12: field test 1 với UAV được cấp (5 kịch bản), stress test VRAM/link/latency + fix,
2 buổi rehearsal + 1 lượt demo end-to-end 10 phút không interrupt (AC11), cập nhật
`docs/` + báo cáo đồ án, W12 là buffer.

## Requirements

**Functional**
- Field test 1: 5 kịch bản (mục tiêu tĩnh 50m; mục tiêu di động cắt 100m; đồng đội GPS cạnh mục tiêu; UAV bay + FOV; cắt link).
- Stress: VRAM <3.8GB/30s khi chạy full; OOM cố tình → `--cpu` khởi động lại OK; 5 vòng cắt/ghép link; SLM warm <1.5s.
- Demo 10 phút đúng kịch bản PDR §7, 1 lượt không interrupt, có ghi hình.
- Tài liệu: `docs/` đồng bộ với hệ cuối; báo cáo đồ án có bảng kết quả AC1–AC11.

**Non-functional**
- Mọi fix trong phase này là surgical — không refactor lớn (code đã ổn định, sắp demo).
- Demo phải chạy được từ 0 trên laptop sạch theo `laptop-deployment-guide.md` (rehearsal = kiểm tra lại guide).

## Architecture

Không component mới — layer test/verify trên hệ đã tích hợp (Phase 4):

```
Field test (W9)          Stress (W10)              Demo (W11)             Docs (W12)
5 kịch bản ngoài field →  nvidia-smi -l 1 30s   →  kịch bản PDR §7      →  docs/ cập nhật
ghi log + video HUD      OOM → --cpu recover    2 rehearsal + 1 chính   →  báo cáo đồ án
issue triage → fix       5× cắt/ghép link       record 10 phút          →  buffer W12
                         SLM latency log        re-verify AC1–AC11
```

Field test checklist: `docs/field-test-checklist.md` (mới) — 5 kịch bản, cột observe/expect/actual.

## Related Code Files

**Create**
- `docs/field-test-checklist.md` — 5 kịch bản field test + stress, cột expect/actual.

**Modify**
- `docs/laptop-deployment-guide.md` — thêm: model 8 class (`--model`), `--source` (RTSP/UVC/file), mục mạng riêng + WireGuard, UAV được cấp.
- `docs/project-overview-pdr.md` — status các mục scope S1–S7 → done/actual; bảng kết quả AC1–AC11 thực đo.
- `docs/hardware-bom.md` — status thật: thiết bị đã dùng (UAV được cấp, laptop, server) vs chưa mua (ESP32 node, v.v.).
- Code fixes (nếu stress phát hiện bug) — sửa tại chỗ, surgical, ghi vào changelog.

**Delete** — không.

## Implementation Steps

1. **W9d1–2** — field test 1 tại thao trường: chạy 5 kịch bản theo
   `docs/field-test-checklist.md`; ghi hình HUD + log console.
2. **W9d3–5** — triage issue: critical (block demo) → fix ngay; minor → W10;
   cập nhật checklist actual.
3. **W10d1** — VRAM: chạy full (model 8c + Ollama) + `nvidia-smi -l 1` 30s → <3.8GB;
   cố tình OOM (mở app nặng) → `--cpu` khởi động lại bình thường — **AC9**.
4. **W10d2** — link loss: 5 vòng cắt/ghép (tắt WG/WiFi node) → mỗi lần local ≤5s, không crash.
5. **W10d3** — latency: SLM warm <1.5s (log `--sim`); chuỗi cảnh báo 360P: vào khung → flash <2s — **AC10**, **AC8**.
6. **W10d4–5** — fix issues W9+W10; re-run test suite (`test_tracking.py`, `test_telemetry_chain.py`,
   `test_vpn_link.py`, `test_degradation_modes.py`) xanh hết.
7. **W11d1–2** — 2 buổi rehearsal kịch bản 10 phút (PDR §7): bật Ollama + HUD → UAV bay/replay
   → box + track id + cone FOV → ~100m cảnh báo (flash + SLM) → đồng đội xanh → rút link →
   local 5s → (bay thật) đổi waypoint. Fix còn sót.
8. **W11d3** — **chạy demo chính thức 1 lượt, ghi hình full 10 phút** — **AC11**.
9. **W11d4** — re-verify AC1–AC11 lần cuối bằng bảng lệnh (mỗi AC 1 lệnh), ghi số đo thực.
10. **W12d1–3** — tài liệu: cập nhật 3 file `docs/` (bước Modify); viết báo cáo đồ án
    (sơ đồ hệ thống, kết quả AC1–AC11, giới hạn công khai: khoảng cách ±30–50%, SLM ~1s,
    không ban đêm, haptic blocked).
11. **W12d4–5** — buffer cho W9–W11 tràn.

## Success Criteria

- [ ] Field test log: 5/5 kịch bản chạy, issue đã triage (critical = 0 còn mở) — M5
- [ ] `nvidia-smi -l 1` 30s đầu chạy full: VRAM <3.8GB; OOM → `--cpu` khởi động lại OK — **AC9**
- [ ] 5 vòng cắt/ghép link: local mode ≤5s, không crash — **AC5**
- [ ] SLM warm <1.5s/call, câu ≤12 từ tiếng Việt — **AC10**
- [ ] Demo 10 phút: 1 lượt không interrupt theo kịch bản PDR §7, có file ghi hình — **AC11**
- [ ] Bảng AC1–AC11: 11/11 PASS với số đo thực (báo cáo đồ án)
- [ ] `docs/` cập nhật: deployment guide (VPN + `--source` + model 8c), PDR status, BOM status

## Risk Assessment

| Rủi ro | Mitigation |
|--------|-----------|
| Field test không bay được UAV (thời tiết/sân) | Kịch bản PDR §7 cho phép "replay video 360P"; field test chạy bằng replay + đồng đội sim, ghi lý do |
| Issue W9 nhiều, ăn hết W10 | W12 là buffer 1 tuần; nếu vẫn thiếu → thu scope demo: replay video thay bay thật (phải giảng viên duyệt) |
| VRAM chặt với model 8c | Cùng kích thước "n" → không đổi VRAM kỳ vọng; `--cpu` là fallback đã chứng minh |
| Demo chính thức gặp sự cố (W11d3) | 2 rehearsal trước; checklist trước-demo từ `laptop-deployment-guide.md` §5; luôn có đường replay video dự phòng trong tay |
| Docs drift (code và tài liệu lệch) | W12 là tuần docs riêng, không để trôi vào buffer; buffer chỉ cho bug |
