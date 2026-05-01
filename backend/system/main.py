import sys
import argparse

# 백엔드에서 넘겨주는 인자들을 받을 준비
parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("--mode")
parser.add_argument("--task_id")
args = parser.parse_args()

print(f"--- 분석 엔진 실행됨 ---")
print(f"URL: {args.url}")
print(f"모드: {args.mode}")
print(f"ID: {args.task_id}")