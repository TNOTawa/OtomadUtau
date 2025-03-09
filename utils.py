def parse_time(time_str):
    """通用时间格式转换"""
    try:
        # 支持两种格式：分:秒.毫秒 或 纯秒数
        if ':' in time_str:
            minutes, seconds = time_str.split(':')
            return float(minutes)*60*1000 + float(seconds)*1000
        return float(time_str)*1000
    except:
        raise ValueError(f"无效时间格式: {time_str}")
