"""极趣云平台 API 客户端"""

from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://cloud.zectrix.com/open/v1"


class APIError(Exception):
    """API 请求错误"""

    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"[{code}] {msg}")


class ZectrixClient:
    def __init__(self, api_key: str):
        self._session = requests.Session()
        self._session.headers["X-API-Key"] = api_key
        self._session.headers["Content-Type"] = "application/json"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
    ) -> Any:
        resp = self._session.request(
            method,
            f"{BASE_URL}{path}",
            params=params,
            json=json_body,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise APIError(data.get("code", -1), data.get("msg", "unknown error"))
        return data.get("data")

    def _upload(
        self,
        path: str,
        *,
        files: dict | None = None,
        data: dict | None = None,
    ) -> Any:
        resp = self._session.post(
            f"{BASE_URL}{path}",
            files=files,
            data=data,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") != 0:
            raise APIError(result.get("code", -1), result.get("msg", "unknown error"))
        return result.get("data")

    # ── 设备管理 ──

    def list_devices(self) -> list[dict]:
        """获取设备列表"""
        return self._request("GET", "/devices")

    # ── 待办事项 ──

    def list_todos(self, *, status: int | None = None, device_id: str | None = None) -> list[dict]:
        """获取待办列表"""
        params: dict = {}
        if status is not None:
            params["status"] = status
        if device_id is not None:
            params["deviceId"] = device_id
        return self._request("GET", "/todos", params=params)

    def create_todo(self, *, title: str, **kwargs) -> dict:
        """创建待办"""
        body: dict = {"title": title}
        body.update(kwargs)
        return self._request("POST", "/todos", json_body=body)

    def update_todo(self, todo_id: int, **kwargs) -> dict:
        """更新待办"""
        return self._request("PUT", f"/todos/{todo_id}", json_body=kwargs)

    def complete_todo(self, todo_id: int) -> None:
        """标记待办完成（再次调用则取消完成）"""
        self._request("PUT", f"/todos/{todo_id}/complete")

    def delete_todo(self, todo_id: int) -> None:
        """删除待办"""
        self._request("DELETE", f"/todos/{todo_id}")

    # ── 显示推送 ──

    def push_image(
        self,
        device_id: str,
        image_paths: list[str],
        *,
        dither: bool = True,
        page_id: str | None = None,
    ) -> dict:
        """推送图片到设备（最多5张，单张不超过2MB）"""
        opened = []
        files: dict = {}
        for path in image_paths:
            f = open(path, "rb")
            opened.append(f)
            files["images"] = ("image", f)
        form_data: dict = {"dither": str(dither).lower()}
        if page_id is not None:
            form_data["pageId"] = page_id
        try:
            result = self._upload(f"/devices/{device_id}/display/image", files=files, data=form_data)
        finally:
            for f in opened:
                f.close()
        return result

    def push_text(
        self,
        device_id: str,
        text: str,
        *,
        font_size: int = 20,
        page_id: str | None = None,
    ) -> dict:
        """推送文本到设备"""
        body: dict = {"text": text, "fontSize": font_size}
        if page_id is not None:
            body["pageId"] = page_id
        return self._request("POST", f"/devices/{device_id}/display/text", json_body=body)

    def push_structured_text(
        self,
        device_id: str,
        *,
        title: str | None = None,
        body: str | None = None,
        page_id: str | None = None,
    ) -> dict:
        """推送标题+正文到设备"""
        payload: dict = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if page_id is not None:
            payload["pageId"] = page_id
        return self._request("POST", f"/devices/{device_id}/display/structured-text", json_body=payload)
