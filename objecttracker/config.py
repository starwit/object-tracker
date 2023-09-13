from pydantic import BaseModel, conint
from pydantic_settings import BaseSettings, SettingsConfigDict
from visionlib.pipeline.settings import LogLevel, YamlConfigSettingsSource


class DeepOcSortConfig(BaseModel):
    det_thresh: float = 0.25
    fp16: bool = False
    model_weights: str = 'osnet_x0_25_msmt17.pt'

class RedisConfig(BaseModel):
    host: str = 'localhost'
    port: conint(ge=1, le=65536) = 6379
    stream_id: str
    input_stream_prefix: str = 'objectdetector'
    output_stream_prefix: str = 'objecttracker'

class ObjectTrackerConfig(BaseSettings):
    log_level: LogLevel = LogLevel.WARNING
    tracking_params: DeepOcSortConfig
    device: str = 'cpu'
    redis: RedisConfig

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)