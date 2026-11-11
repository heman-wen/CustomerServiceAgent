
from pathlib import Path

from src.rag.parsers.mineru_client import MinerUClient


def main():
    project_root = Path(__file__).resolve().parents[3]

    input_file = (
        project_root / "data" / "raw" / "after_sales_policy.docx"
    )

    output_dir = (
        project_root / "data" / "parsed" / "after_sales_policy"
    )

    print("===== MinerU V4 文档解析测试 =====")

    client = MinerUClient()

    result_dir = client.parse_file(
        file_path=str(input_file),
        output_dir=str(output_dir),
    )

    print("\n===== 解析完成 =====")
    print(f"结果目录：{result_dir}")

    markdown_files = list(result_dir.rglob("full.md"))

    if markdown_files:
        print(f"\n找到 Markdown 文件：{markdown_files[0]}")

        content = markdown_files[0].read_text(
            encoding="utf-8"
        )

        print("\n===== 解析内容预览 =====")
        print(content[:2000])
    else:
        print("没有找到 full.md，请检查解压后的文件目录。")


if __name__ == "__main__":
    main()
