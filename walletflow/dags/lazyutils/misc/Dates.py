from datetime import datetime, timedelta

#TODO Implement unit tests
def deltatime_to_strftime(delta: int, fmt: str = '%Y-%m-%d %H:%M:%S'):
    dt = datetime.now() - timedelta(days=delta)
    return dt.strftime(fmt)

def now_strftime(fmt: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(fmt)
