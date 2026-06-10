"""成绩计算工具"""
import math


def percentage_to_letter(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def letter_to_points(letter: str) -> float:
    mapping = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    if letter not in mapping:
        raise ValueError(f"无效的等级: {letter}")
    return mapping[letter]


def score_to_gpa(score: float) -> float:
    letter = percentage_to_letter(score)
    return letter_to_points(letter)


def calculate_gpa(grades: list) -> float:
    if not grades:
        return 0.0
    total_points = 0
    total_credits = 0
    for g in grades:
        gpa = score_to_gpa(g["score"])
        total_points += gpa * g["credit"]
        total_credits += g["credit"]
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def calculate_variance(scores: list) -> float:
    if len(scores) < 2:
        return 0.0
    avg = sum(scores) / len(scores)
    variance = sum((s - avg) ** 2 for s in scores) / (len(scores) - 1)
    return round(variance, 2)


def calculate_std(scores: list) -> float:
    if len(scores) < 2:
        return 0.0
    return round(math.sqrt(calculate_variance(scores)), 2)


def calculate_grade_distribution(records: list) -> dict:
    dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for record in records:
        if record.grades:
            for g in record.grades:
                letter = percentage_to_letter(g.score)
                dist[letter] = dist.get(letter, 0) + 1
    return dist


def is_honor_roll(score: float, total_credits: float) -> bool:
    return score >= 85 and total_credits >= 10


def calculate_median(scores: list) -> float:
    if not scores:
        return 0.0
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    mid = n // 2
    if n % 2 == 0:
        return round((sorted_scores[mid - 1] + sorted_scores[mid]) / 2, 2)
    return round(sorted_scores[mid], 2)


def calculate_highest_lowest(scores: list) -> dict:
    if not scores:
        return {"highest": 0, "lowest": 0, "difference": 0}
    highest = max(scores)
    lowest = min(scores)
    return {"highest": highest, "lowest": lowest, "difference": round(highest - lowest, 2)}


def calculate_pass_rate(grades: list) -> float:
    if not grades:
        return 0.0
    passed = sum(1 for g in grades if g >= 60)
    return round(passed / len(grades), 2)


def percentile_rank(score: float, scores: list) -> float:
    if not scores:
        return 0.0
    if len(scores) == 1:
        return 100.0
    below = sum(1 for s in scores if s < score)
    return round((below / (len(scores) - 1)) * 100, 2)