from fastapi import FastAPI,HTTPException,APIRouter,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_control import crud, mymodels
from models.params import caseSearchData, setCaseData, userEntryData, userData, strategyData, talentSearchData
import json
from modules import mdlCommon, mdlSearchCase, mdlUserAction, mdlStrategy, mdlTalent, mdlVectorstore

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, itnavi(FastAPI)"}

@router.get("/allIssues")
def get_industry():
    # 業界情報の取得
    status, result = mdlCommon.getAllIssues()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/cases/featured")
def select_featured_case_list():
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getFeaturedCaseList()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/searchCase")
def create_search_case(data:caseSearchData):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.createSearchCase(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/searchCaseDirect")
def create_search_case(data:caseSearchData):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.createSearchCase(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/cases")
def select_case_list(search_id: int, search_id_sub: int):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getCaseList(search_id, search_id_sub)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/case")
def update_search_case(data:setCaseData):
    # 選択ケースを登録
    status, result = mdlSearchCase.updateSearchCase(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/caseDetail")
def select_case_detail(search_id: int, search_id_sub: int):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlSearchCase.getCaseDetail(search_id, search_id_sub)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/job")
def get_job():
    # 職種情報の取得
    status, result = mdlCommon.getJob()
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/searchTalent")
def create_search_case(data:talentSearchData):
    # 検索ID/検索サブID発行、検索履歴登録
    status, result = mdlTalent.createSearchTalent(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/searchResults")
def select_talent(search_id: int, search_id_sub: int):
    # 人材情報を取得
    status, result = mdlTalent.getTalent(search_id, search_id_sub)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/userEntry")
def update_search_case(data:userEntryData):
    # ユーザー情報を登録
    status, result = mdlUserAction.createUser(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/agentSupport")
def create_agent_support(data:userData):
    # エージェント相談情報を登録し担当へメール通知
    status, result = mdlUserAction.createRequest(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/strategy")
def create_strategy(data:userData):
    # 戦略文書を作成
    status, result = mdlStrategy.createDoc(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/strategy")
def select_strategy(search_id: int, search_id_sub: int, document_id: int):
    # 戦略文書を取得
    status, result = mdlStrategy.getDoc(search_id, search_id_sub, document_id)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/strategy/dl")
def create_strategy(data:strategyData):
    # 戦略文書を作成
    status, result = mdlStrategy.updateDocDl(data)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.post("/createVecrorstore{target}")
def create_vector_store(target:str):
    # FAISSインデックスの再作成
    status, result = mdlVectorstore.createVectorstore(target)
    return JSONResponse(content=json.loads(result), status_code=status)

@router.get("/searchTalentByPrompt{prompt,cnt}")
def get_talent_by_prompt(prompt: str, cnt:int):
    # 人材情報を取得
    status, result = mdlTalent.getTalentByPrompt(prompt,cnt)
    return JSONResponse(content=result, status_code=status)

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