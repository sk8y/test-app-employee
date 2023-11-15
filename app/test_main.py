# flake8: noqa

import os
from fastapi import FastAPI, HTTPException, Request, Response
import uuid
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
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


from .main import app

client = TestClient(app)


def test_get_load():
    response = client.get("/api/v1/load")
    assert response.status_code == 200
    assert response.json()['rows_loaded'] > 100


def test_get_employee_100():
    response = client.get("/api/v1/employee/100")
    assert response.status_code == 200
    assert response.json()['data'][0]['employee_id'] == 100


def test_get_employee_9999():
    response = client.get("/api/v1/employee/9999")
    assert response.status_code == 200
    assert response.json()['data'] == []


def test_get_employee_xxxx():
    response = client.get("/api/v1/employee/xxxx")
    assert response.status_code != 200


def test_get_first_name():
    response = client.get("/api/v1/employee/first_name/Karma")
    assert response.status_code == 200
    assert response.json()['data'][0]['first_name'] == 'Karma'


def test_get_first_name_empty():
    response = client.get("/api/v1/employee/first_name/xxxx")
    assert response.status_code == 200
    assert response.json()['data'] == []

def test_get_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
