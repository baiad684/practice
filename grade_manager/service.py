"""业务逻辑层"""
from grade_manager.models import Student, Grade, StudentRecord
from grade_manager import calculator


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


def get_student_statistics(records: list, student_id: str) -> dict:
    record = get_student_record(records, student_id)
    avg = calculate_average(record)
    gpa_data = [{'score': g.score, 'credit': g.credit} for g in record.grades]
    gpa = calculator.calculate_gpa(gpa_data) if gpa_data else 0.0
    pf = get_pass_fail(record)
    total_credit = calculate_total_credit(record)
    return {
        'student_id': student_id,
        'name': record.student.name,
        'average': avg,
        'gpa': gpa,
        'pass_fail': pf,
        'total_credit': total_credit,
        'grade_count': len(record.grades)
    }


def get_course_average(records: list, course: str) -> dict:
    scores = []
    for r in records:
        for g in r.grades:
            if g.course == course:
                scores.append(g.score)
    if not scores:
        return {'course': course, 'student_count': 0, 'average': 0.0}
    avg = round(sum(scores) / len(scores), 2)
    variance = calculator.calculate_variance(scores)
    std = calculator.calculate_std(scores)
    dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for s in scores:
        letter = calculator.percentage_to_letter(s)
        dist[letter] += 1
    return {'course': course, 'student_count': len(scores), 'average': avg, 'variance': variance, 'std': std, 'distribution': dist}


def clear_all_records(records: list) -> int:
    count = len(records)
    records.clear()
    return count


def batch_create_students(records: list, students_data: list) -> dict:
    created = 0
    failed = 0
    errors = []
    for data in students_data:
        try:
            add_student(records, data['student_id'], data['name'], data['age'], data['class_name'])
            created += 1
        except ValueError as e:
            failed += 1
            errors.append(str(e))
    return {'created': created, 'failed': failed, 'errors': errors}


def batch_delete_students(records: list, student_ids: list) -> dict:
    deleted = 0
    not_found = 0
    for sid in student_ids:
        if remove_student(records, sid):
            deleted += 1
        else:
            not_found += 1
    return {'deleted': deleted, 'failed': not_found}


def add_grade_with_notes(records: list, student_id: str, course: str, score: float, credit: float, notes: str = '') -> Grade:
    if score < 0 or score > 100:
        raise ValueError(f'成绩必须在0-100之间，当前: {score}')
    for r in records:
        if r.student.student_id == student_id:
            grade = Grade(student_id, course, score, credit)
            r.grades.append(grade)
            return grade
    raise ValueError(f'找不到学生 {student_id}')


def get_student_grade_detail(records: list, student_id: str) -> dict:
    record = get_student_record(records, student_id)
    grade_list = []
    for g in record.grades:
        grade_list.append({
            'course': g.course,
            'score': g.score,
            'credit': g.credit,
            'letter': calculator.percentage_to_letter(g.score),
            'gpa': calculator.score_to_gpa(g.score)
        })
    return {
        'student_id': student_id,
        'name': record.student.name,
        'grades': grade_list,
        'total_credit': calculate_total_credit(record)
    }


def search_students(records: list, keyword: str) -> list:
    results = []
    for r in records:
        if keyword in r.student.student_id or keyword in r.student.name or keyword in r.student.class_name:
            results.append(r)
    return results


def get_class_statistics(records: list, class_name: str) -> dict:
    class_records = [r for r in records if r.student.class_name == class_name]
    if not class_records:
        return {'class_name': class_name, 'student_count': 0}
    avgs = [calculate_average(r) for r in class_records]
    total_credits = sum(calculate_total_credit(r) for r in class_records)
    return {
        'class_name': class_name,
        'student_count': len(class_records),
        'average': round(sum(avgs) / len(avgs), 2),
        'total_credits': total_credits
    }


def get_overview(records: list) -> dict:
    total_students = len(records)
    total_grades = sum(len(r.grades) for r in records)
    all_scores = []
    for r in records:
        for g in r.grades:
            all_scores.append(g.score)
    all_grade_data = [{'score': g.score, 'credit': g.credit} for r in records for g in r.grades]
    classes = list(set(r.student.class_name for r in records))
    return {
        'total_students': total_students,
        'total_grades': total_grades,
        'total_classes': len(classes),
        'classes': classes,
        'overall_average': round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0,
        'overall_gpa': calculator.calculate_gpa(all_grade_data) if all_grade_data else 0.0,
        'grade_distribution': calculator.calculate_grade_distribution(records) if records else {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    }
