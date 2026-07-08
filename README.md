[코드 설명]

_enable_dpi_awareness()
Windows 고해상도 모니터에서 tkinter 창이 흐릿하게 보이는 문제를 막기 위한 함수다. ctypes를 이용해 Windows API의 DPI 인식 모드를 설정한다. Per-Monitor DPI Aware 설정이 실패하면 구버전 방식(SetProcessDPIAware)으로 대체 시도하고, 그마저 실패해도 무시하고 넘어가도록 예외 처리가 되어 있다. Windows가 아닌 환경에서는 아예 실행되지 않는다.

parse_stl(file_path)
STL 파일에는 ASCII 형식과 바이너리 형식 두 가지가 있는데, 이 함수가 어떤 형식인지 자동으로 판별한다. 바이너리 STL은 앞의 80바이트가 헤더, 그다음 4바이트가 삼각형 개수, 이후 삼각형 하나당 50바이트(법선벡터 12바이트+정점 3개×12바이트+속성 2바이트)로 구성된다는 규격을 이용해, 파일 크기와 "예상되는 바이너리 크기"를 비교한다. 두 값이 일치하면 바이너리로 판단해 _parse_binary_stl을 호출하고, 그렇지 않으면 ASCII 형식으로 간주해 _parse_ascii_stl을 호출한다.

_parse_binary_stl(f, triangle_count)
struct.unpack("<12fH", data)로 각 삼각형의 50바이트를 한 번에 해석한다. 앞 3개 float는 법선벡터라 버리고, 그다음 9개 float가 세 정점의 (x,y,z) 좌표다. 모든 정점을 순회하면서 축별 최솟값(min_xyz)과 최댓값(max_xyz)을 갱신해 나간다. 이 최소/최대값의 차이가 곧 모델의 바운딩 박스 크기가 된다.

_parse_ascii_stl(file_path)
ASCII STL은 vertex x y z 형태의 텍스트 줄로 좌표가 기록되어 있다. 파일을 한 줄씩 읽으면서 "vertex"로 시작하는 줄만 골라 좌표를 추출하고, 바이너리 파싱과 동일한 방식으로 min/max를 갱신한다.

_format_result(file_path)
파싱 결과로 얻은 min/max 좌표의 차이를 계산해 가로(X)/세로(Y)/높이(Z) 크기를 구하고, 파일명과 함께 보기 좋은 문자열로 정리해 반환한다.

main()
전체 흐름을 담당한다. tkinter 창을 숨긴 채로(root.withdraw()) 파일 선택 대화상자만 반복해서 띄우는 구조다. 여러 파일을 한 번에 선택할 수 있게 askopenfilenames를 사용했고, 각 파일에 대해 _format_result를 호출하되 오류가 나더라도 프로그램 전체가 멈추지 않도록 try/except로 개별 처리한다. 모든 결과를 모아 콘솔 출력과 팝업으로 동시에 보여준 뒤, 계속할지 묻는 대화상자로 반복 여부를 결정한다.
