from celery.result import AsyncResult  # type: ignore[import-untyped]

from internal.celery_tasks.celery_init import app


def main():
    result = AsyncResult(
        "4f7a7081-1205-4b7e-911a-6d84bb99c630",
        app=app,
    )
    print("self.app.backend", app.backend)
    print("result:", result)
    print("result.status:", result.status)
    print("result.name:", result.name)


if __name__ == "__main__":
    main()