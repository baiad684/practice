"""Web API 测试"""
import pytest
from fastapi.testclient import TestClient
from grade_manager.api import app, records

# 注意：测试会修改全局 records，每次测试前清理
@pytest.fixture(autouse=True)
def clean_records():
    from grade_manager.api import records as global_records
    global_records.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def create_student(client):
    def _create(sid, name, age=20, cls="软工2401"):
        resp = client.post("/students", params={
            "student_id": sid, "name": name, "age": age, "class_name": cls
        })
        return resp.json() if resp.status_code == 200 else None
    return _create


class TestCreateStudent:
    def test_create_student_success(self, client, create_student):
        result = create_student("S001", "张三")
        assert result["message"] == "创建成功"
        assert result["student_id"] == "S001"

    def test_create_duplicate_student(self, client, create_student):
        create_student("S001", "张三")
        resp = client.post("/students", params={
            "student_id": "S001", "name": "张三2", "age": 20, "class_name": "软工2401"
        })
        assert resp.status_code == 400
        assert "已存在" in resp.json()["detail"]


class TestDeleteStudent:
    def test_delete_existing_student(self, client, create_student):
        create_student("S001", "张三")
        resp = client.delete("/students/S001")
        assert resp.status_code == 200
        assert resp.json()["message"] == "删除成功"

    def test_delete_nonexistent_student(self, client):
        resp = client.delete("/students/S999")
        assert resp.status_code == 404
        assert "不存在" in resp.json()["detail"]


class TestAddGrade:
    def test_add_grade_success(self, client, create_student):
        create_student("S001", "张三")
        resp = client.post("/grades", params={
            "student_id": "S001", "course": "高等数学",
            "score": 95, "credit": 4.0
        })
        assert resp.status_code == 200
        assert resp.json()["grade"]["score"] == 95

    def test_add_grade_invalid_score(self, client, create_student):
        create_student("S001", "张三")
        resp = client.post("/grades", params={
            "student_id": "S001", "course": "高等数学",
            "score": 150, "credit": 4.0
        })
        assert resp.status_code == 400
        assert "0-100" in resp.json()["detail"]

    def test_add_grade_nonexistent_student(self, client):
        resp = client.post("/grades", params={
            "student_id": "S999", "course": "高等数学",
            "score": 90, "credit": 4.0
        })
        assert resp.status_code == 400
        assert "找不到学生" in resp.json()["detail"]


class TestGetStudentInfo:
    def test_get_student_info(self, client, create_student):
        create_student("S001", "张三")
        client.post("/grades", params={
            "student_id": "S001", "course": "高数", "score": 90, "credit": 4.0
        })
        resp = client.get("/students/S001/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["student"]["name"] == "张三"
        assert data["average"] == 90.0
        assert data["grade_count"] == 1

    def test_get_nonexistent_student(self, client):
        resp = client.get("/students/S999/info")
        assert resp.status_code == 404


class TestGetRanking:
    def test_get_ranking(self, client, create_student):
        create_student("S001", "张三")
        create_student("S002", "李四")
        client.post("/grades", params={"student_id": "S001", "course": "高数", "score": 95, "credit": 4.0})
        client.post("/grades", params={"student_id": "S002", "course": "高数", "score": 85, "credit": 4.0})
        resp = client.get("/students/S001/ranking")
        assert resp.status_code == 200
        assert resp.json()["rank"] == 1

    def test_get_ranking_not_found(self, client):
        resp = client.get("/students/S999/ranking")
        assert resp.status_code == 404
