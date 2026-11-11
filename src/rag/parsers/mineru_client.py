
import time
import zipfile
from pathlib import Path

import requests

from src.rag.config import (
    MINERU_API_KEY,
    MINERU_BASE_URL,
    MINERU_MODEL_VERSION,
    MINERU_POLL_INTERVAL,
    MINERU_MAX_WAIT_SECONDS,
)


class MinerUClient:
    """MinerU V4 文档解析客户端。"""

    def __init__(self):
        if not MINERU_API_KEY:
            raise ValueError("缺少 MINERU_API_KEY，请检查 .env")

        self.base_url = MINERU_BASE_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {MINERU_API_KEY}",
            "Content-Type": "application/json",
        }

    def upload_file(self, file_path: str) -> str:
        """申请上传地址，并上传本地文件，返回 batch_id。"""

        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"文件不存在：{path}")

        supported_extensions = {
            ".pdf", ".doc", ".docx", ".ppt", ".pptx",
            ".png", ".jpg", ".jpeg", ".jp2",
            ".webp", ".gif", ".bmp", ".html",
        }

        if path.suffix.lower() not in supported_extensions:
            raise ValueError(
                f"MinerU V4 暂不支持该文件格式：{path.suffix}"
            )

        if path.stat().st_size == 0:
            raise ValueError("不能上传空文件")

        if path.stat().st_size > 200 * 1024 * 1024:
            raise ValueError("文件超过 200MB")

        # 1. 申请上传地址
        request_url = f"{self.base_url}/file-urls/batch"

        payload = {
            "files": [
                {
                    "name": path.name,
                    "data_id": path.stem,
                }
            ],
            "model_version": MINERU_MODEL_VERSION,
        }

        response = requests.post(
            request_url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:
            raise RuntimeError(
                f"申请上传地址失败：{result.get('msg')}"
            )

        data = result["data"]
        batch_id = data["batch_id"]
        file_urls = data["file_urls"]

        if not file_urls:
            raise RuntimeError("MinerU 没有返回上传地址")

        # 2. 上传文件
        # 注意：签名上传地址不需要携带 MinerU API Key
        with path.open("rb") as file:
            upload_response = requests.put(
                file_urls[0],
                data=file,
                timeout=300,
            )

        upload_response.raise_for_status()

        print(f"文件上传成功：{path.name}")
        print(f"Batch ID：{batch_id}")

        return batch_id

    def wait_for_result(self, batch_id: str) -> str:
        """轮询任务，完成后返回解析结果 ZIP 地址。"""

        query_url = (
            f"{self.base_url}/extract-results/batch/{batch_id}"
        )

        start_time = time.time()

        while time.time() - start_time < MINERU_MAX_WAIT_SECONDS:

            response = requests.get(
                query_url,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()

            if result.get("code") != 0:
                raise RuntimeError(
                    f"查询解析任务失败：{result.get('msg')}"
                )

            extract_results = (
                result.get("data", {}).get("extract_result", [])
            )

            if not extract_results:
                print("等待 MinerU 创建解析任务...")
                time.sleep(MINERU_POLL_INTERVAL)
                continue

            item = extract_results[0]
            state = item.get("state")

            print(f"当前解析状态：{state}")

            if state == "done":
                zip_url = item.get("full_zip_url")

                if not zip_url:
                    raise RuntimeError("解析完成，但没有返回 ZIP 地址")

                return zip_url

            if state == "failed":
                raise RuntimeError(
                    f"文档解析失败：{item.get('err_msg')}"
                )

            time.sleep(MINERU_POLL_INTERVAL)

        raise TimeoutError("MinerU 解析超时，请稍后重新查询任务")

    def download_and_extract(
        self,
        zip_url: str,
        output_dir: str,
    ) -> Path:
        """下载 ZIP 并解压，返回解压目录。"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        zip_path = output_path / "mineru_result.zip"

        # 签名下载地址直接使用，不附加 API Key
        response = requests.get(
            zip_url,
            timeout=300,
        )
        response.raise_for_status()

        zip_path.write_bytes(response.content)

        if not zipfile.is_zipfile(zip_path):
            raise RuntimeError("MinerU 返回的文件不是有效 ZIP")

        extract_dir = output_path / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as archive:
            # 防止 ZIP 中的路径穿越
            for member in archive.infolist():
                target = (extract_dir / member.filename).resolve()

                if (
                    target != extract_dir.resolve()
                    and extract_dir.resolve() not in target.parents
                ):
                    raise RuntimeError("ZIP 中包含不安全的文件路径")

            archive.extractall(extract_dir)

        print(f"解析结果已保存到：{extract_dir}")

        return extract_dir

    def parse_file(
        self,
        file_path: str,
        output_dir: str,
    ) -> Path:
        """完整流程：上传、等待、下载和解压。"""

        batch_id = self.upload_file(file_path)

        zip_url = self.wait_for_result(batch_id)

        return self.download_and_extract(
            zip_url,
            output_dir,
        )
