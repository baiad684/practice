"""service.py 单元测试"""
import pytest
from grade_manager.models import Student, Grade, StudentRecord
from grade_manager import service


@pytest.fixture
def sample_records():
    records = []
    service.add_student(records, "S001", "张三", 20, "软工2401")
    service.add_student(records, "S002", "李四", 21, "软工2401")
    service.add_student(records, "S003", "王五", 19, "计科2401")
    return records


class TestAddStudent:
    def test_add_student_success(self, sample_records):
        record = service.add_student(sample_records, "S004", "赵六", 20, "计科2401")
        assert record.student.name == "赵六"
        assert len(sample_records) == 4

    def test_add_duplicate_student(self, sample_records):
        with pytest.raises(ValueError, match="S001 已存在"):
            service.add_student(sample_records, "S001", "张三副本", 20, "软工2401")

    def test_add_student_creces_with_grades(self, sample_records):
        record = service.add_student(sample_records, "S005", "钱七", 22, "软工2401")
        assert record.grades == []


class TestRemoveStudent:
    def test_remove_existing_student(self, sample_records):
        assert service.remove_student(sample_records, "S001") is True
        assert len(sample_records) == 2

    def test_remove_nonexistent_student(self, sample_records):
        assert service.remove_student(sample_records, "S999") is False
        assert len(sample_records) == 3


class TestAddGrade:
    def test_add_grade_success(self, sample_records):
        grade = service.add_grade(sample_records, "S001", "高等数学", 95, 4.0)
        assert grade.score == 95
        assert grade.course == "高等数学"
        assert len(sample_records[0].grades) == 1

    def test_add_grade_invalid_score_low(self, sample_records):
        with pytest.raises(ValueError, match="必须在0-100"):
            service.add_grade(sample_records, "S001", "高等数学", -5, 4.0)

    def test_add_grade_invalid_score_high(self, sample_records):
        with pytest.raises(ValueError, match="必须在0-100"):
            service.add_grade(sample_records, "S001", "高等数学", 101, 4.0)

    def test_add_grade_nonexistent_student(self, sample_records):
        with pytest.raises(ValueError, match="找不到学生"):
            service.add_grade(sample_records, "S999", "高等数学", 90, 4.0)

    def test_add_multiple_grades(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S001", "英语", 85, 3.0)
        assert len(sample_records[0].grades) == 2


class TestGetStudentRecord:
    def test_find_existing_student(self, sample_records):
        record = service.get_student_record(sample_records, "S002")
        assert record.student.student_id == "S002"

    def test_find_nonexistent_student(self, sample_records):
        with pytest.raises(ValueError, match="找不到学生"):
            service.get_student_record(sample_records, "S999")


class TestCalculateAverage:
    def test_calculate_average_with_grades(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S001", "英语", 80, 3.0)
        avg = service.calculate_average(sample_records[0])
        # (90*4 + 80*3) / (4+3) = 600/7 ≈ 85.71
        assert avg == pytest.approx(85.71)

    def test_calculate_average_no_grades(self, sample_records):
        assert service.calculate_average(sample_records[0]) == 0.0

    def test_calculate_average_single_grade(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 95, 4.0)
        assert service.calculate_average(sample_records[0]) == 95.0


class TestCalculateTotalCredit:
    def test_total_credit_sum(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S001", "英语", 80, 3.0)
        assert service.calculate_total_credit(sample_records[0]) == 7.0

    def test_total_credit_no_grades(self, sample_records):
        assert service.calculate_total_credit(sample_records[0]) == 0.0


class TestGetPassFail:
    def test_all_pass(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S001", "英语", 85, 3.0)
        result = service.get_pass_fail(sample_records[0])
        assert result == {"passed": 2, "failed": 0, "total": 2}

    def test_with_failures(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S001", "英语", 55, 3.0)
        result = service.get_pass_fail(sample_records[0])
        assert result == {"passed": 1, "failed": 1, "total": 2}

    def test_no_grades(self, sample_records):
        result = service.get_pass_fail(sample_records[0])
        assert result == {"passed": 0, "failed": 0, "total": 0}

    def test_all_fail(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 40, 4.0)
        result = service.get_pass_fail(sample_records[0])
        assert result == {"passed": 0, "failed": 1, "total": 1}


class TestClassAverage:
    def test_class_average(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 90, 4.0)
        service.add_grade(sample_records, "S002", "高数", 80, 4.0)
        avg = service.get_class_average(sample_records, "软工2401")
        assert avg == pytest.approx(85.0)

    def test_class_no_match(self, sample_records):
        assert service.get_class_average(sample_records, "不存在班级") == 0.0


class TestRanking:
    def test_ranking_order(self, sample_records):
        service.add_grade(sample_records, "S001", "高数", 95, 4.0)
        service.add_grade(sample_records, "S002", "高数", 85, 4.0)
        service.add_grade(sample_records, "S003", "高数", 75, 4.0)
        ranking = service.get_ranking(sample_records)
        assert ranking[0]["rank"] == 1
        assert ranking[0]["average"] == 95.0
        assert ranking[2]["average"] == 75.0
