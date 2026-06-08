import math

"""calculator.py 单元测试"""
import pytest
from grade_manager import calculator


class TestPercentageToLetter:
    def test_a_grade(self):
        assert calculator.percentage_to_letter(95) == 'A'
        assert calculator.percentage_to_letter(90) == 'A'

    def test_b_grade(self):
        assert calculator.percentage_to_letter(85) == 'B'
        assert calculator.percentage_to_letter(80) == 'B'

    def test_c_grade(self):
        assert calculator.percentage_to_letter(75) == 'C'
        assert calculator.percentage_to_letter(70) == 'C'

    def test_d_grade(self):
        assert calculator.percentage_to_letter(65) == 'D'
        assert calculator.percentage_to_letter(60) == 'D'

    def test_f_grade(self):
        assert calculator.percentage_to_letter(59) == 'F'
        assert calculator.percentage_to_letter(0) == 'F'

    def test_boundary_90(self):
        assert calculator.percentage_to_letter(90) == 'A'

    def test_boundary_60(self):
        assert calculator.percentage_to_letter(60) == 'D'


class TestLetterToPoints:
    def test_valid_letters(self):
        assert calculator.letter_to_points("A") == 4.0
        assert calculator.letter_to_points("B") == 3.0
        assert calculator.letter_to_points("C") == 2.0
        assert calculator.letter_to_points("D") == 1.0
        assert calculator.letter_to_points("F") == 0.0

    def test_invalid_letter(self):
        with pytest.raises(ValueError, match="无效的等级"):
            calculator.letter_to_points("X")


class TestScoreToGpa:
    def test_full_score(self):
        assert calculator.score_to_gpa(95) == 4.0

    def test_low_score(self):
        assert calculator.score_to_gpa(50) == 0.0

    def test_boundary_score(self):
        assert calculator.score_to_gpa(80) == 3.0
        assert calculator.score_to_gpa(70) == 2.0


class TestCalculateGpa:
    def test_gpa_calculation(self):
        grades = [
            {'score': 95, 'credit': 4.0},
            {'score': 80, 'credit': 3.0},
        ]
        gpa = calculator.calculate_gpa(grades)
        # (4.0*4 + 3.0*3) / 7 = 25/7 = 3.57
        assert gpa == pytest.approx(3.57)

    def test_gpa_empty_grades(self):
        assert calculator.calculate_gpa([]) == 0.0

    def test_gpa_zero_credit(self):
        grades = [{'score': 90, 'credit': 0.0}]
        assert calculator.calculate_gpa(grades) == 0.0


class TestCalculateVariance:
    def test_variance_calculation(self):
        scores = [80, 85, 90, 95, 100]
        var = calculator.calculate_variance(scores)
        assert var == pytest.approx(62.5)

    def test_variance_single_score(self):
        assert calculator.calculate_variance([90]) == 0.0

    def test_variance_all_same(self):
        assert calculator.calculate_variance([85, 85, 85]) == 0.0


class TestCalculateStd:
    def test_std_calculation(self):
        scores = [80, 85, 90, 95, 100]
        std = calculator.calculate_std(scores)
        assert std == pytest.approx(7.91)

    def test_std_single_score(self):
        assert calculator.calculate_std([90]) == 0.0


class TestGradeDistribution:
    def test_distribution(self, mocker):
        from grade_manager.models import StudentRecord, Student, Grade
        grades_data = [(95, 4.0), (85, 3.0), (72, 3.0), (55, 2.0)]
        record = StudentRecord(Student("S001", "Test", 20, "Class1"))
        for score, credit in grades_data:
            record.grades.append(Grade("S001", "Course", score, credit))
        result = calculator.calculate_grade_distribution([record])
        assert result == {"A": 1, "B": 1, "C": 1, "D": 0, "F": 1}


class TestIsHonorRoll:
    def test_honor_roll(self):
        assert calculator.is_honor_roll(90, 12) is True

    def test_not_honor_roll_low_score(self):
        assert calculator.is_honor_roll(80, 12) is False

    def test_not_honor_roll_low_credit(self):
        assert calculator.is_honor_roll(90, 5) is False
