"""
STL 파일 크기(가로/세로/높이) 확인 프로그램

실행하면 파일 탐색기 창이 열려 STL 파일을 선택할 수 있고,
선택한 파일의 이름과 바운딩 박스 크기(X/Y/Z, mm 단위 가정)를 알려준다.
"""

import os
import struct
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


def _enable_dpi_awareness():
    """Windows 고해상도(HiDPI) 모니터에서 파일 탐색기 창이 흐리게 보이는 문제를 해결한다."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-Monitor DPI Aware
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def parse_stl(file_path):
    """STL 파일(ASCII/바이너리 모두 지원)을 읽어 (min_xyz, max_xyz)를 반환한다."""
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        header = f.read(80)
        count_bytes = f.read(4)
        if len(count_bytes) == 4:
            (triangle_count,) = struct.unpack("<I", count_bytes)
        else:
            triangle_count = 0

        expected_binary_size = 84 + 50 * triangle_count

        if file_size == expected_binary_size and triangle_count > 0:
            return _parse_binary_stl(f, triangle_count)

    # 바이너리 형식이 아니면 ASCII로 간주하고 다시 읽는다.
    return _parse_ascii_stl(file_path)


def _parse_binary_stl(f, triangle_count):
    min_xyz = [float("inf")] * 3
    max_xyz = [float("-inf")] * 3

    for _ in range(triangle_count):
        data = f.read(50)
        if len(data) < 50:
            break
        # 법선벡터(3f) + 정점 3개(각 3f) + attribute(2바이트)
        values = struct.unpack("<12fH", data)
        vertices = values[3:12]  # 정점 9개 float (v1x,v1y,v1z, v2x,v2y,v2z, v3x,v3y,v3z)
        for i in range(3):
            x, y, z = vertices[i * 3 : i * 3 + 3]
            for axis, val in enumerate((x, y, z)):
                if val < min_xyz[axis]:
                    min_xyz[axis] = val
                if val > max_xyz[axis]:
                    max_xyz[axis] = val

    return min_xyz, max_xyz


def _parse_ascii_stl(file_path):
    min_xyz = [float("inf")] * 3
    max_xyz = [float("-inf")] * 3

    with open(file_path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("vertex"):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    for axis, val in enumerate((x, y, z)):
                        if val < min_xyz[axis]:
                            min_xyz[axis] = val
                        if val > max_xyz[axis]:
                            max_xyz[axis] = val

    return min_xyz, max_xyz


def _format_result(file_path):
    min_xyz, max_xyz = parse_stl(file_path)
    width, depth, height = (max_xyz[i] - min_xyz[i] for i in range(3))
    file_name = os.path.basename(file_path)
    return (
        f"파일 이름: {file_name}\n"
        f"  가로 (X): {width:.2f} mm\n"
        f"  세로 (Y): {depth:.2f} mm\n"
        f"  높이 (Z): {height:.2f} mm"
    )


def main():
    _enable_dpi_awareness()

    root = tk.Tk()
    root.withdraw()

    while True:
        file_paths = filedialog.askopenfilenames(
            title="크기를 확인할 STL 파일을 선택하세요 (여러 개 선택 가능)",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")],
        )

        if not file_paths:
            break

        results = []
        for file_path in file_paths:
            try:
                results.append(_format_result(file_path))
            except Exception as e:
                results.append(f"파일 이름: {os.path.basename(file_path)}\n  오류: {e}")

        summary = "\n\n".join(results)

        print("=" * 40)
        print(summary)
        print("=" * 40)

        if not messagebox.askyesno("계속", "다른 STL 파일도 확인하시겠습니까?"):
            break


if __name__ == "__main__":
    main()
