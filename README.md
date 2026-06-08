# 学生成绩管理系统

## 项目说明

这是一个简易的学生成绩管理系统

## 功能

- 学生管理（增/删/查）
- 成绩管理（添加成绩）
- 成绩计算（平均分、GPA、排名、分布等）
- RESTful API 接口

## 技术栈

- Python 3.8+
- pytest（单元测试）
- FastAPI（Web API）
- Requests/HTTPX（API 测试）

## 安装

```bash
pip install -r requirements.txt
```

## 运行 API 服务

```bash
uvicorn grade_manager.api:app --reload
```

## 运行测试

```bash
pytest tests/ -v
```
