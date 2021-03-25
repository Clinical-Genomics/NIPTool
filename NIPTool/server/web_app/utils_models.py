from pydantic import BaseModel
from typing import Dict, Literal, Optional


def WarningModel(BaseModel):
    value: Optional[float] ##handel can be str when empty
    warn: str

def SampleInfoModel(BaseModel):
    sample_id: str
    FF: WarningModel
    CNVSegment: WarningModel
    FFX: WarningModel
    FFY: WarningModel
    Zscore_13: WarningModel
    Zscore_18: WarningModel
    Zscore_21: WarningModel
    Zscore_X: Dict[str, float]
    Status: str
    Include: bool
    Comment:str
    Last_Change: str
    
    
def WarningColorModel(BaseModel):
    FF_Formatted: Literal['warning', 'default', 'danger']
    Zscore_13: Literal['warning', 'default', 'danger']
    Zscore_18: Literal['warning', 'default', 'danger']
    Zscore_21: Literal['warning', 'default', 'danger']