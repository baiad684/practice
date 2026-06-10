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


@app.delete("/students/batch")
def batch_delete(data: dict):
    ids = data.get("student_ids", [])
    result = service.batch_delete_students(records, ids)
    return result


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



@app.get("/students")
def get_all_students():
    students = service.get_all_students(records)
    return {"students": [s.__dict__ for s in students]}


@app.post("/grades/with-notes")
def add_grade_with_notes(student_id: str, course: str, score: float, credit: float, notes: str = ""):
    try:
        grade = service.add_grade_with_notes(records, student_id, course, score, credit, notes)
        return {"message": "成绩添加成功", "grade": grade.__dict__, "notes": notes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/grades/{student_id}/{course}")
def delete_grade(student_id: str, course: str):
    try:
        record = service.get_student_record(records, student_id)
        original_len = len(record.grades)
        record.grades = [g for g in record.grades if g.course != course]
        if len(record.grades) == original_len:
            raise HTTPException(status_code=404, detail=f"课程 {course} 不存在")
        return {"message": "成绩删除成功"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/grades/{student_id}/{course}")
def update_grade(student_id: str, course: str, score: float, credit: float):
    try:
        record = service.get_student_record(records, student_id)
        for g in record.grades:
            if g.course == course:
                if score < 0 or score > 100:
                    raise HTTPException(status_code=400, detail="成绩必须在0-100之间")
                g.score = score
                g.credit = credit
                return {"message": "成绩修改成功", "grade": g.__dict__}
        raise HTTPException(status_code=404, detail=f"课程 {course} 不存在")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/students/{student_id}/grades")
def get_student_all_grades(student_id: str):
    try:
        detail = service.get_student_grade_detail(records, student_id)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/students/{student_id}/statistics")
def get_student_statistics(student_id: str):
    try:
        stats = service.get_student_statistics(records, student_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/students/{student_id}/honor")
def get_honor_roll_status(student_id: str):
    try:
        record = service.get_student_record(records, student_id)
        total_credit = service.calculate_total_credit(record)
        avg = service.calculate_average(record)
        honor = calculator.is_honor_roll(avg, total_credit)
        return {"student_id": student_id, "honor_roll": honor, "average": avg, "total_credits": total_credit}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/course/average/{course}")
def get_course_avg(course: str):
    result = service.get_course_average(records, course)
    return result


@app.get("/course/distribution/{course}")
def get_course_distribution(course: str):
    result = service.get_course_average(records, course)
    return {"course": course, "distribution": result.get("distribution", {}), "count": result.get("student_count", 0)}


@app.post("/students/batch-create")
def batch_create(data: dict):
    students_data = data.get("students", [])
    result = service.batch_create_students(records, students_data)
    return result


@app.get("/class/summary")
def get_class_summary(class_name: str = ""):
    if not class_name:
        classes = list(set(r.student.class_name for r in records))
        summaries = []
        for cls in classes:
            summaries.append(service.get_class_statistics(records, cls))
        return {"classes": summaries}
    result = service.get_class_statistics(records, class_name)
    return result


@app.post("/records/clear")
def clear_records():
    count = service.clear_all_records(records)
    return {"message": "记录已清空", "cleared_count": count}


@app.get("/dashboard/overview")
def get_overview():
    return service.get_overview(records)


@app.get("/students/search")
def search_students(keyword: str):
    results = service.search_students(records, keyword)
    return {"keyword": keyword, "results": results, "count": len(results)}
