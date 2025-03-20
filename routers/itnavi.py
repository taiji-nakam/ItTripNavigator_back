from fastapi import FastAPI,HTTPException,APIRouter,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_control import crud, mymodels
from models.params import caseSearchData,setCaseData
import json
from modules import mdlCommon,mdlSearchCase

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, itnavi(FastAPI)"}

@router.get("/allIssues​")
def get_industry():
    # 業界情報の取得
    status, result = mdlCommon.getAllIssues()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/searchCase")
def create_search_case(data:caseSearchData):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.createSearchCase(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/cases{search_id,search_id_sub}")
def select_case_list(search_id: int, search_id_sub: int):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getCaseList(search_id, search_id_sub)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/cases/featured")
def select_featured_case_list():
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getFeaturedCaseList()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/case")
def update_search_case(data:setCaseData):
    # 選択ケースを登録
    status, result = mdlSearchCase.updateSearchCase(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/caseDetail{search_id,search_id_sub}")
def select_case_detail(search_id: int, search_id_sub: int):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getCaseDetail(search_id, search_id_sub)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/industry")
def get_industry():
    # 業界情報の取得
    status, result = mdlCommon.getIndustry()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/company_size")
def get_company_size():
    # 業界情報の取得
    status, result = mdlCommon.getCompanySize()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/department")
def get_department():
    # 業界情報の取得
    status, result = mdlCommon.getDepartment()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/theme")
def get_theme():
    # 業界情報の取得
    status, result = mdlCommon.getTheme()
    return JSONResponse(content=json.loads(result), status_code=status)