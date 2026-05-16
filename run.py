"""开发服务器启动入口"""
import subprocess
import sys


def main():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        check=True,
    )


if __name__ == "__main__":
    main()
