from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from cache import set_cache, is_stale
from services.stock import get_current_price, get_chart_data
from services.supply import get_supply_demand
from services.community import get_community_sentiment

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def refresh_price():
    try:
        data = get_current_price()
        set_cache("price", data)
        logger.info(f"Price updated: {data['price']}")
    except Exception as e:
        logger.error(f"Price refresh failed: {e}")

def refresh_charts():
    try:
        for period in ["annual", "monthly", "weekly"]:
            data = get_chart_data(period)
            set_cache(f"chart_{period}", data)
        logger.info("Charts updated")
    except Exception as e:
        logger.error(f"Chart refresh failed: {e}")

def refresh_supply():
    try:
        data = get_supply_demand()
        set_cache("supply", data)
        logger.info(f"Supply updated: foreigner={data['foreigner']}")
    except Exception as e:
        logger.error(f"Supply refresh failed: {e}")

def refresh_community():
    try:
        data = get_community_sentiment()
        set_cache("community", data)
        logger.info(f"Community updated: score={data['sentiment_score']}")
    except Exception as e:
        logger.error(f"Community refresh failed: {e}")

def start_scheduler():
    scheduler.add_job(refresh_price, IntervalTrigger(seconds=60), id="price", replace_existing=True)
    scheduler.add_job(refresh_charts, IntervalTrigger(minutes=5), id="charts", replace_existing=True)
    scheduler.add_job(refresh_supply, IntervalTrigger(minutes=3), id="supply", replace_existing=True)
    scheduler.add_job(refresh_community, IntervalTrigger(minutes=10), id="community", replace_existing=True)

    # 앱 시작 시 즉시 1회 실행
    refresh_price()
    refresh_charts()
    refresh_supply()
    refresh_community()

    scheduler.start()
    logger.info("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
