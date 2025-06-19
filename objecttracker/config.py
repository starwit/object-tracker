from enum import Enum
from typing import Union

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated
from visionlib.pipeline.settings import LogLevel, YamlConfigSettingsSource


class TrackingAlgorithm(str, Enum):
    OCSORT = 'OCSORT'

class DeepOcSortConfig(BaseModel):
    model_weights: str
    device: str
    fp16: bool
    per_class: bool
    det_thresh: float
    max_age: int
    min_hits: int
    iou_threshold: float
    delta_t: int
    asso_func: str
    inertia: float
    w_association_emb: float
    alpha_fixed_emb: float
    aw_param: float
    embedding_off: bool
    cmc_off: bool
    aw_off: bool
    new_kf_off: bool

class OcSortConfig(BaseModel):
    det_thresh: float = 0.2
    max_age: int = 30
    min_hits: int = 3
    asso_threshold: float = 0.3
    delta_t: int = 3
    asso_func: str = 'iou'
    inertia: float = 0.2
    use_byte: bool = False
    Q_xy_scaling: float = 0.01
    Q_s_scaling: float = 0.0001

class RedisConfig(BaseModel):
    host: str = 'localhost'
    port: Annotated[int, Field(ge=1, le=65536)] = 6379
    stream_id: str
    input_stream_prefix: str = 'objectdetector'
    output_stream_prefix: str = 'objecttracker'

class ObjectTrackerConfig(BaseSettings):
    log_level: LogLevel = LogLevel.WARNING
    tracker_config: Union[DeepOcSortConfig, OcSortConfig] = OcSortConfig()
    tracker_algorithm: TrackingAlgorithm = TrackingAlgorithm.OCSORT
    redis: RedisConfig
    prometheus_port: Annotated[int, Field(gt=1024, le=65536)] = 8000

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)