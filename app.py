from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    PicklePersistence,
)
from ptbcontrib.ptb_jobstores.sqlalchemy import PTBSQLAlchemyJobStore

import grpc
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk import metrics as sdkmetrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource

from src.custom_filters import filter_bot_added
from src.logging import tg_logger
from src import handlers
import os


temporality_delta = {
    sdkmetrics.Counter: AggregationTemporality.DELTA,
    sdkmetrics.UpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.Histogram: AggregationTemporality.DELTA,
    sdkmetrics.ObservableCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableUpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableGauge: AggregationTemporality.DELTA,
}


def main():
    dsn = os.environ.get("UPTRACE_DSN")

    exporter = OTLPMetricExporter(
        endpoint="otlp.uptrace.dev:4317",
        headers=(("uptrace-dsn", dsn),),
        timeout=5,
        compression=grpc.Compression.Gzip,
        preferred_temporality=temporality_delta,
    )
    reader = PeriodicExportingMetricReader(exporter)

    resource = Resource(
        attributes={
            "service.name": "wachter",
            "service.version": "1.1.0",
            "deployment.environment": os.environ.get("DEPLOYMENT_ENVIRONMENT"),
        }
    )
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(provider)

    application = (
        ApplicationBuilder()
        .persistence(PicklePersistence(filepath="persistent_storage.pickle"))
        .token(os.environ["TELEGRAM_TOKEN"])
        .build()
    )
    if "PERSISTENCE_DATABASE_URL" in os.environ:
        application.job_queue.scheduler.add_jobstore(
            PTBSQLAlchemyJobStore(
                application=application,
                url=os.environ["PERSISTENCE_DATABASE_URL"],
            )
        )

    application.add_handler(CommandHandler("help", handlers.help_handler))
    application.add_handler(CommandHandler("listjobs", handlers.list_jobs_handler))

    # group UX
    application.add_handler(
        ChatMemberHandler(
            handlers.my_chat_member_handler,
            ChatMemberHandler.MY_CHAT_MEMBER,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Entity("hashtag") & filters.ChatType.GROUPS,
            handlers.on_hashtag_message,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS & filter_bot_added,
            handlers.on_new_chat_members,
        )
    )

    # admin UX
    application.add_handler(CommandHandler("start", handlers.start_handler))
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    application.add_handler(MessageHandler(filters.TEXT, handlers.message_handler))
    application.add_error_handler(handlers.error_handler)

    application.job_queue.run_repeating(
        handlers.group.group_handler.db_metrics_reader_helper, 3600, name="metrics_exporter"
    )

    tg_logger.info("Bot has started successfully")
    application.run_polling()


if __name__ == "__main__":
    main()
