from enum import Enum

from pydantic import BaseModel


class LogLevel(str, Enum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'

class DeepOcSortConfig(BaseModel):
    det_thresh: float
    fp16: bool = False
    model_weights: str

class ObjectTrackerConfig(BaseModel):
    log_level: LogLevel = LogLevel.WARNING
    tracking_params: DeepOcSortConfig
    device: str