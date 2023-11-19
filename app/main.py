# flake8: noqa

import os
from fastapi import FastAPI, HTTPException, Request, Response
import uuid
from fastapi.responses import RedirectResponse
import logging
import datetime
from redis_om import (
    Field,
    HashModel,
    Migrator
)
from redis_om import get_redis_connection
import csv
from fastapi.testclient import TestClient
from starlette_exporter import PrometheusMiddleware, handle_metrics



app_name = 'employee'
app = FastAPI(title=app_name, version='0.0.1', description=app_name, swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})
app.add_middleware(
    PrometheusMiddleware,
    app_name=app_name,
    prefix='app',
    labels={
      "service": "employee",
    },
    group_paths=True,
    buckets=[0.1, 0.5, 1, 2.5, 10],
    skip_paths=['/docs', '/openapi.json', '/'],
    skip_methods=['OPTIONS'],
    )
app.add_route("/metrics", handle_metrics)

logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)8s] %(name)s %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('API is starting up http://127.0.0.1:8000/')


class Employee(HashModel):
    employee_id: int = Field(index=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    gender: str
    birth_date: datetime.date
    employee_type: str
    salary: float
    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "birth_date": self.birth_date.isoformat(),
            "employee_type": self.employee_type,
            "salary": self.salary
        }


def load_data() -> int:
    row_count = 0
    with open('employee.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                print(row)
                emp = Employee(
                        employee_id = i + 1,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        gender=row.get('gender', 'M'),
                        birth_date=datetime.date.fromisoformat(row['birth_date']),
                        employee_type=row.get('employee_type', 'temporary'),
                        salary=row.get('salary', 0.0))
                emp.save()
                row_count += 1
    Migrator().run()
    return row_count


@app.get("/")
async def root():
    return RedirectResponse("/docs")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/v1/load")
async def load(request: Request, response: Response):
    request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    response.headers["x-response-id"] = request_id
    row_count = 0
    try:
        row_count = load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail="exception: {}".format(e))
    retval = {
            "response_id": request_id,
            "rows_loaded": row_count
    }
    return retval


@app.get("/api/v1/unload")
async def unload(request: Request, response: Response):
    request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    response.headers["x-response-id"] = request_id
    db_flushed = False
    try:
        redis_conn = Employee.db()
        redis_conn.flushall()
        db_flushed = True
    except Exception as e:
        raise HTTPException(status_code=500, detail="exception: {}".format(e))

    retval = {
            "response_id": request_id,
            "db_flushed": db_flushed
    }
    return retval


@app.get("/api/v1/employee/{employee_id}")
async def get_employee(
        request: Request, response: Response, employee_id: int):
    request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    response.headers["x-response-id"] = request_id
    retval = {
            "response_id": request_id,
            "data": []
        }
    try:
        retval['data'] = [ e.to_dict() for e in Employee.find(Employee.employee_id == employee_id).all() ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="exception: {}".format(e))
    return retval


@app.get("/api/v1/employee/first_name/{first_name}")
async def get_employee_first_name(
        request: Request, response: Response, first_name: str):
    request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    response.headers["x-response-id"] = request_id
    retval = {
            "response_id": request_id,
            "data": []
        }
    try:
        retval['data'] = [ e.to_dict() for e in Employee.find(Employee.first_name == first_name).all() ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="exception: {}".format(e))
    return retval


@app.get("/api/v1/employee/last_name/{last_name}")
async def get_employee_last_name(
        request: Request, response: Response, last_name: str):
    request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    response.headers["x-response-id"] = request_id
    retval = {
            "response_id": request_id,
            "data": []
        }
    try:
        retval['data'] = [ e.to_dict() for e in Employee.find(Employee.last_name == last_name).all() ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="exception: {}".format(e))
    return retval


@app.on_event("startup")
async def startup():
    Employee.Meta.database = get_redis_connection(
        url=os.getenv('REDIS_URL', 'redis://redis:6379'),
        decode_responses=True)
    try:
        e = Employee.find(Employee.employee_id == 999).all()
    except:
        e = []
    print(e)
    if len(e) == 0:
        logger.info('loading data')
        load_data()

