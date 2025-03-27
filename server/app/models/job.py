from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import time


class JobStatus(BaseModel):
    """작업 상태 모델"""

    job_id: str
    image_id: str
    status: str
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))
    params: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SparkJobSubmission(BaseModel):
    """스파크 작업 제출 모델"""

    job_name: str
    main_class: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    jar_files: List[str] = Field(default_factory=list)
    py_files: List[str] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    driver_memory: str = "1g"
    executor_memory: str = "1g"
    num_executors: int = 2
    executor_cores: int = 1
