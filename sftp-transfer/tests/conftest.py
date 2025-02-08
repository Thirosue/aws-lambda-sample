import os
import sys

# 現在の conftest.py の絶対パスを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
# プロジェクトルート（tests ディレクトリの1つ上のフォルダ）を取得 → /src
project_root = os.path.abspath(os.path.join(current_dir, ".."))
# src ディレクトリの絶対パスを取得 → /src/src
src_dir = os.path.join(project_root, "src")

# プロジェクトルートを sys.path に追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# src ディレクトリも sys.path に追加
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
