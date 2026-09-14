# upstream/extractors

upstream 원본에서 `upstream/normalized/`를 만드는 추출기입니다(06 §5, §12 검사 1). 표준 라이브러리만 씁니다.

## 실행 (저장소 루트에서)

```sh
python3 -m upstream.extractors extract            # lock 커밋 기준으로 normalized/ 재생성
python3 -m upstream.extractors check              # 재추출해 커밋된 파일과 비교 — 06 §12 검사 1
python3 -m upstream.extractors diff --upstream im-not-ai --commit <sha>   # 다른 커밋에서 무엇이 바뀌는지
python3 -m upstream.extractors validate           # upstream/interface/ 규칙 검사
```

원본은 `upstream/.cache/<이름>@<lock 커밋>/` 클론에서 `git show <commit>:<path>`로 읽으므로 체크아웃 없이 어느 커밋이든 추출할 수 있습니다.

## 구성

| 파일 | 역할 |
|---|---|
| `source.py` | lock 읽기, 커밋별 파일 읽기, `AnchorNotFound` |
| `markdown.py` | 블록 파서와 앵커 형식 (코드블록 인식, 제목 깊이 무관, 태그, 표, 인용, 목록, 문단) |
| `normalized.py` | normalized YAML 쓰기와 읽기, 해시 |
| `validate.py` | `upstream/interface/*.schema.yaml` 규칙 검사 |
| `<upstream>.py` | upstream 하나의 선택 규칙. `extract(commit)`이 `({normalized 상대 경로: 텍스트}, 실패 목록)`을 돌려줍니다 |

## 새 upstream을 넣는 규약

1. `upstream/interface/`의 스키마에서 역할을 고릅니다. 스키마는 고치지 않습니다.
2. `upstream/extractors/<이름>.py`에 `NAME`과 `extract(commit)`을 둡니다. 파일 전체를 블록으로 받으면 `markdown.parse`, 일부만 고르면 제목·번호·굵은 라벨로 찾는 함수를 씁니다. 찾지 못하면 `AnchorNotFound`를 올리지 말고 실패 목록에 `(id, 이유)`를 넣습니다.
3. 조각마다 `normalized.fragment_lines`로 출처를 붙입니다. 문장을 바꾸면 `adapted`와 `original`이 필요합니다.
4. `__main__.py`의 `MODULES`에 등록하고 `extract`, `validate`, `check`을 돌립니다. lock.yaml에 있는데 `MODULES`에 없는 upstream이 있으면 모든 명령이 실패합니다.
