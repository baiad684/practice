"""Web API 接口层"""
from fastapi import FastAPI, HTTPException
from typing import List
from grade_manager.models import Student, Grade, StudentRecord
from grade_manager import service, calculator

app = FastAPI(title="学生成绩管理系统 API")

# 内存存储
records: list = []


@app.post("/students")
def create_student(student_id: str, name: str, age: int, class_name: str):
    try:
        record = service.add_student(records, student_id, name, age, class_name)
        return {"message": "创建成功", "student_id": record.student.student_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    result = service.remove_student(records, student_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")
    return {"message": "删除成功"}


@app.post("/grades")
def add_grade(student_id: str, course: str, score: float, credit: float):
    try:
        grade = service.add_grade(records, student_id, course, score, credit)
        return {"message": "成绩添加成功", "grade": grade.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/students/{student_id}/info")
def get_student_info(student_id: str):
    try:
        record = service.get_student_record(records, student_id)
        avg = service.calculate_average(record)
        return {
            "student": record.student.__dict__,
            "average": avg,
            "grade_count": len(record.grades)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/students/{student_id}/ranking")
def get_student_ranking(student_id: str):
    try:
        ranking = service.get_ranking(records)
        for r in ranking:
            if r["student_id"] == student_id:
                return r
        raise HTTPException(status_code=404, detail="学生不在排名中")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
