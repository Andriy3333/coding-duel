from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class TimeComplexity(BaseModel):
    code: str


class TimeComplexityResponse(BaseModel):
    time_complexity: str


class TestCaseResult(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    actual_output: Optional[str]
    passed: bool
    error: Optional[str]
    execution_time: Optional[float]

class CodeTestResult(BaseModel):
    message: str
    code: str
    opponent_id: str
    player_name: str
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str]
    complexity: Optional[str]
    implement_time: Optional[int]
    final_time: Optional[int]

class PlayerFinalStats(BaseModel):
    player_name: str
    player_id: str
    implement_time: int
    time_complexity: str
    final_time: int



class RunTestCasesRequest(BaseModel):
    player_id: str
    code: str
    language: str
    question_name: str  # Changed from test_cases to question_name
    timeout: Optional[int] = 5
    timer: int


class RunTestCasesResponse(BaseModel):
    success: bool
    test_results: List[TestCaseResult]
    total_passed: int
    total_failed: int
    error: Optional[str]


class DockerRunRequest(BaseModel):
    code: str
    language: str
    test_input: dict
    timeout: int = 5
    function_name: Optional[str] = "solution"  # Default to "solution" for backward compatibility


class TestCase(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    is_hidden: bool


class StarterCode(BaseModel):
    python: str
    javascript: str
    java: str
    cpp: str


class SolutionApproach(BaseModel):
    time_complexity: str
    space_complexity: str
    approach: str


class QuestionMetadata(BaseModel):
    acceptance_rate: str
    total_accepted: str
    total_submissions: str
    created_at: str
    last_updated: str


class QuestionData(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: Optional[List[str]] = None
    description_html: str
    starter_code: StarterCode
