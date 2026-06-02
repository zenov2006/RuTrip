from fastapi import APIRouter
from schemas import GottenInfo, SearchResponse
from service import normalize_text, detect_tags, get_ai_recommendation

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search(info: GottenInfo):
    search_query = info.query if info.query is not None else ""

    clean_words = normalize_text(search_query)
    new_tags = detect_tags(clean_words)
    
    final_tags = list(set((info.tags or []) + new_tags))

    ai_data = await get_ai_recommendation(search_query, final_tags)
    
    return {
        "status": "success",
        "query": info.query,
        "detected_tags": final_tags,
        "ai_recommendation": ai_data.get("text"),
        "regions": ai_data.get("regions", [])
    }

@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok", "module": "ml_module"}