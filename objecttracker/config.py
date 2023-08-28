import os
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from pydantic import BaseModel, conint
from pydantic.fields import FieldInfo
from pydantic_settings import (BaseSettings, PydanticBaseSettingsSource,
                               SettingsConfigDict)


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    Taken from https://docs.pydantic.dev/latest/usage/pydantic_settings/#adding-sources
    """

    def __init__(self, settings_cls: type[BaseSettings]):
        super().__init__(settings_cls)
        try:
            self.settings_dict = yaml.load(Path(os.environ.get('SETTINGS_FILE', 'settings.yaml')).read_text('utf-8'), Loader=yaml.Loader)
        except FileNotFoundError:
            self.settings_dict = defaultdict(lambda: None)
            print('settings.yaml not found. Using defaults.')

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        field_value = self.settings_dict[field_name]
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d
    

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

class RedisConfig(BaseModel):
    host: str
    port: conint(ge=1, le=65536)
    stream_id: str

class ObjectTrackerConfig(BaseSettings):
    log_level: LogLevel = LogLevel.WARNING
    tracking_params: DeepOcSortConfig
    device: str
    redis: RedisConfig = None

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, YamlConfigSettingsSource(settings_cls), file_secret_settings)