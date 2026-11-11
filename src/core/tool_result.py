def success(data=None, message="操作成功"):
    """工具执行成功"""
    return {
        "success": True,
        "status": "success",
        "data": data,
        "message": message,
    }


def not_found(message="没有找到相关数据"):
    """目标数据不存在"""
    return {
        "success": True,
        "status": "not_found",
        "data": None,
        "message": message,
    }


def failed(message="工具执行失败"):
    """工具执行过程中发生错误"""
    return {
        "success": False,
        "status": "failed",
        "data": None,
        "message": message,
    }


def unknown(message="当前无法判断"):
    """数据不足，无法得出业务结论"""
    return {
        "success": True,
        "status": "unknown",
        "data": None,
        "message": message,
    }