"""业务逻辑层"""
from grade_manager.models import Student, Grade, StudentRecord


def add_student(records: list, student_id: str, name: str, age: int, class_name: str) -> StudentRecord:
    for r in records:
        if r.student.student_id == student_id:
            raise ValueError(f"学生 {student_id} 已存在")
    student = Student(student_id, name, age, class_name)
    record = StudentRecord(student)
    records.append(record)
    return record


def remove_student(records: list, student_id: str) -> bool:
    for i, r in enumerate(records):
        if r.student.student_id == student_id:
            records.pop(i)
            return True
    return False


def add_grade(records: list, student_id: str, course: str, score: float, credit: float) -> Grade:
    for r in records:
        if r.student.student_id == student_id:
            if score < 0 or score > 100:
                raise ValueError(f"成绩必须在0-100之间，当前: {score}")
            grade = Grade(student_id, course, score, credit)
            r.grades.append(grade)
            return grade
    raise ValueError(f"找不到学生 {student_id}")


def get_student_record(records: list, student_id: str) -> StudentRecord:
    for r in records:
        if r.student.student_id == student_id:
            return r
    raise ValueError(f"找不到学生 {student_id}")


def get_all_students(records: list) -> list:
    return [r.student for r in records]


def calculate_average(record: StudentRecord) -> float:
    if not record.grades:
        return 0.0
    total = sum(g.score * g.credit for g in record.grades)
    total_credit = sum(g.credit for g in record.grades)
    if total_credit == 0:
        return 0.0
    return round(total / total_credit, 2)


def calculate_total_credit(record: StudentRecord) -> float:
    return sum(g.credit for g in record.grades)


def get_pass_fail(record: StudentRecord) -> dict:
    if not record.grades:
        return {"passed": 0, "failed": 0, "total": 0}
    passed = sum(1 for g in record.grades if g.score >= 60)
    failed = sum(1 for g in record.grades if g.score < 60)
    return {"passed": passed, "failed": failed, "total": len(record.grades)}


def get_class_average(records: list, class_name: str) -> float:
    class_records = [r for r in records if r.student.class_name == class_name]
    if not class_records:
        return 0.0
    avgs = [calculate_average(r) for r in class_records]
    return round(sum(avgs) / len(avgs), 2)


def get_ranking(records: list) -> list:
    data = [(r.student.name, r.student.student_id, calculate_average(r)) for r in records]
    data.sort(key=lambda x: x[2], reverse=True)
    ranking = []
    for i, (name, sid, avg) in enumerate(data, 1):
        ranking.append({"rank": i, "name": name, "student_id": sid, "average": avg})
    return ranking
