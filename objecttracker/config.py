from pydantic import BaseModel

class DeepOcSortConfig(BaseModel):
    pass

class ObjectTrackerConfig(BaseModel):
    tracking_algorithm: DeepOcSortConfig