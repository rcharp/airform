from app.app import create_celery_app

celery = create_celery_app()


@celery.task()
def api_task():
    return
