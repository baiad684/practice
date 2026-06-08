"""数据模型"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Student:
    student_id: str
    name: str
    age: int
    class_name: str


@dataclass
class Grade:
    student_id: str
    course: str
    score: float
    credit: float


@dataclass
class StudentRecord:
    student: Student
    grades: List[Grade] = field(default_factory=list)
