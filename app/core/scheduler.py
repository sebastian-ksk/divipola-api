import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from scripts.collect_data import main as collect_data_main

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_collect_data():
    """Ejecuta el script de recolección de datos"""
    try:
        logger.info("=" * 50)
        logger.info("Iniciando recolección de datos...")
        await collect_data_main()
        logger.info("Recolección de datos completada exitosamente")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Error en recolección de datos: {e}", exc_info=True)


def start_scheduler():
    """Inicia el scheduler con las tareas programadas"""
    # Ejecutar al iniciar (después de 60 segundos para dar tiempo a que la BD esté lista)
    run_date = datetime.now() + timedelta(seconds=60)
    scheduler.add_job(
        run_collect_data,
        trigger="date",
        run_date=run_date,
        id="collect_data_on_startup",
        max_instances=1,
        replace_existing=True
    )
    logger.info(f"Recolección inicial programada para: {run_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar cada semana (lunes a las 2:00 AM)
    scheduler.add_job(
        run_collect_data,
        trigger=CronTrigger(day_of_week="mon", hour=2, minute=0),
        id="collect_data_weekly",
        max_instances=1,
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler iniciado - Recolección de datos programada para cada lunes a las 2:00 AM")


def shutdown_scheduler():
    """Detiene el scheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")

