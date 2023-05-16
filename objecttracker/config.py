from pydantic import BaseModel

class DeepOcSortConfig(BaseModel):
    det_thresh: float
    fp16: bool = False
    model_weights: str

class ObjectTrackerConfig(BaseModel):
    tracking_params: DeepOcSortConfig
    device: str