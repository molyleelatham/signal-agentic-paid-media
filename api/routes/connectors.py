"""Connector health — live status for frontend header."""

from fastapi import APIRouter
from pydantic import BaseModel

from shared.utils.settings import settings

router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])


class ConnectorStatus(BaseModel):
    id: str
    label: str
    status: str  # active | degraded | inactive
    sync: str
    note: str
    type: str = ""
    endpoint: str = ""


class ConnectorsHealthResponse(BaseModel):
    api: str
    connectors: list[ConnectorStatus]


def _google_ads_configured() -> bool:
    return bool(
        settings.google_ads_developer_token
        and settings.google_ads_client_id
        and settings.google_ads_client_secret
        and settings.google_ads_refresh_token
        and settings.google_ads_customer_id
    )


def _status(configured: bool, live: bool = False) -> str:
    if live:
        return "active"
    if configured:
        return "degraded"
    return "inactive"


@router.get("/status", response_model=ConnectorsHealthResponse)
async def connectors_status(probe: bool = False):
    """Live connector status for the UI header. Use ?probe=true for live API probes."""
    connectors: list[ConnectorStatus] = []

    # —— Tavily ——
    tavily_configured = bool(settings.tavily_api_key)
    tavily_live = False
    tavily_note = "Set TAVILY_API_KEY in .env.local"
    if tavily_configured:
        tavily_note = "API key configured"
        if probe:
            try:
                from services.intelligence.tavily_client import TavilyClient

                client = TavilyClient()
                try:
                    resp = await client.search_and_answer("gymshark", max_results=1)
                    tavily_live = bool(resp.results)
                    tavily_note = f"Live · {len(resp.results)} result(s)"
                finally:
                    await client.close()
            except Exception as exc:
                tavily_note = f"Call failed: {str(exc)[:80]}"
        else:
            tavily_note = "Key OK · use Research to query"

    connectors.append(
        ConnectorStatus(
            id="tavily",
            label="TAVILY WEB CRAWL",
            status=_status(tavily_configured, tavily_live),
            sync="connected" if tavily_live else ("configured" if tavily_configured else "no API key"),
            note=tavily_note,
            type="Web crawl + extract",
            endpoint="api.tavily.com/search",
        )
    )

    # —— Meta MCP ——
    meta_token = bool(settings.meta_ads_access_token)
    meta_mcp_live = False
    meta_mcp_note = "MCP bridge ready · demo placement"
    if probe:
        try:
            from services.platform_integration.mcp_connectors import MetaMCPConnector

            conn = MetaMCPConnector(demo_mode=not meta_token)
            meta_mcp_live = conn.demo_mode or meta_token
            meta_mcp_note = (
                "Live MCP · Marketing API token set"
                if meta_token
                else "Demo MCP · set META_ADS_ACCESS_TOKEN for live"
            )
        except Exception as exc:
            meta_mcp_note = f"MCP error: {str(exc)[:60]}"
    elif meta_token:
        meta_mcp_note = "Token configured · MCP + Graph API"

    connectors.append(
        ConnectorStatus(
            id="meta_mcp",
            label="META MCP",
            status=_status(True, meta_mcp_live or meta_token),
            sync="connected" if meta_token else "demo mode",
            note=meta_mcp_note,
            type="Creative placement · MCP",
            endpoint=settings.meta_mcp_endpoint,
        )
    )

    # —— Google Ads API ——
    gads_configured = _google_ads_configured()
    gads_live = False
    gads_note = "Set GOOGLE_ADS_* OAuth vars in .env.local"
    if gads_configured:
        gads_note = "OAuth credentials configured"
        if probe:
            try:
                from services.platform_integration.google_ads_manager import GoogleAdsManager

                mgr = GoogleAdsManager(
                    developer_token=settings.google_ads_developer_token,
                    client_id=settings.google_ads_client_id,
                    client_secret=settings.google_ads_client_secret,
                    refresh_token=settings.google_ads_refresh_token,
                    customer_id=settings.google_ads_customer_id,
                    demo_mode=False,
                )
                gads_live = not mgr.demo_mode
                gads_note = (
                    f"Live · customer {settings.google_ads_customer_id}"
                    if gads_live
                    else "Credentials set · client init failed (demo fallback)"
                )
            except Exception as exc:
                gads_note = f"Init failed: {str(exc)[:70]}"
        else:
            gads_note = f"Ready · customer {settings.google_ads_customer_id}"
    else:
        try:
            from services.platform_integration.google_ads_manager import GoogleAdsManager

            GoogleAdsManager(demo_mode=True)
            gads_note = "Demo mode · keyword & campaign stubs"
        except Exception:
            pass

    connectors.append(
        ConnectorStatus(
            id="google_ads",
            label="GOOGLE ADS API",
            status=_status(gads_configured, gads_live) if gads_configured else "degraded",
            sync="live" if gads_live else ("configured" if gads_configured else "demo"),
            note=gads_note,
            type="Search + PMax campaigns",
            endpoint="googleads.googleapis.com",
        )
    )

    # —— Meta Ads Manager (Marketing API) ——
    ads_mgr_note = "Set META_ADS_ACCESS_TOKEN for live spend sync"
    if meta_token:
        ads_mgr_note = "Marketing API token configured · campaigns sync"
    connectors.append(
        ConnectorStatus(
            id="ads_manager",
            label="ADS MANAGER API",
            status=_status(meta_token, meta_token and probe),
            sync="connected" if meta_token else "not connected",
            note=ads_mgr_note,
            type="Meta Business · campaign mgmt",
            endpoint="graph.facebook.com/v19.0",
        )
    )

    # —— Reddit (via Tavily research pipeline) ——
    reddit_live = False
    reddit_note = "Requires TAVILY_API_KEY for subreddit scrape"
    if tavily_configured:
        reddit_note = "Pipeline ready · r/fitness · r/Gymshark"
        if probe and tavily_live:
            reddit_live = True
            reddit_note = "Live · Tavily Reddit scrape in GymsharkTavilyResearch"
        elif tavily_configured:
            reddit_note = "Configured · run Tavily research for posts"

    connectors.append(
        ConnectorStatus(
            id="reddit",
            label="REDDIT",
            status=_status(tavily_configured, reddit_live),
            sync="via Tavily" if tavily_configured else "inactive",
            note=reddit_note,
            type="Community signals · scrape",
            endpoint="reddit.com · Tavily proxy",
        )
    )

    # —— Thrad BERT ——
    thrad_key = bool(settings.thrad_api_key)
    thrad_live = False
    thrad_note = "DisBERT + Thrad integrator · demo inference"
    if probe:
        try:
            from services.intelligence.thrad_bert_client import ThradBERTClient
            from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator

            client = ThradBERTClient(demo_mode=not thrad_key)
            DisBERTThradAdIntegrator()
            thrad_live = True
            thrad_note = (
                "Live · Thrad API key + DisBERT classifier"
                if thrad_key
                else "Demo · DisBERT/Thrad pipeline active"
            )
        except Exception as exc:
            thrad_note = f"Load failed: {str(exc)[:60]}"
    elif thrad_key:
        thrad_note = "THRAD_API_KEY set · keyword classify ready"

    connectors.append(
        ConnectorStatus(
            id="thrad",
            label="THRAD",
            status=_status(True, thrad_live or thrad_key),
            sync="connected" if thrad_key else "demo",
            note=thrad_note,
            type="DistilBERT · intent classify",
            endpoint="thrad.ai · DisBERT bridge",
        )
    )

    return ConnectorsHealthResponse(api="online", connectors=connectors)
