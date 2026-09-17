# gate

gate 실행 파일 자리입니다. 시대 02에서는 **아무것도 싣지 않습니다** (`design/02-validation/3-spec/09_toolkit_spec.md` §19).

- gate는 로거나 측정 도구와 파일을 나누지 않는 별도 실행 파일입니다. 로거에 gate를 붙이면 `print` 한 줄로 세션을 막는 코드가 되므로, 자리를 처음부터 따로 둡니다.
- 설계는 09 §19에 있습니다: `Stop` hook으로 도는 실행 파일, 자체 재시도 횟수, `policy × gate` 네 갈래 비교.
- 레코드에는 `gate_on`, `gate_fired`, `gate_retries`, `gate_fired_on` 자리만 예약돼 있고 시대 02에서는 쓰지 않습니다.
- `gate:`를 여는 것은 시대 03 이후입니다.
