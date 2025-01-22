from typing import Any

import orjson
from starlette.responses import JSONResponse


class CustomORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        code, message, data, error = 0, "", None, None

        # 处理 HTTPException
        if isinstance(content, dict) and "detail" in content:
            code = content.get("status_code", 400)
            error = content.get("detail")
            message = "error"
            data = None
        # 处理正常响应
        elif isinstance(content, dict):
            code = content.pop("code", code)
            message = content.pop("message", "ok")
            data = content.pop("data", None) or content
            error = content.pop("error", None)
        else:
            data = content

        response_content = {"code": code, "message": message, "data": data, "error": error}

        return orjson.dumps(response_content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)
