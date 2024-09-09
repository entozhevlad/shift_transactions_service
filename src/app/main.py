from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from src.app.routers.transaction import router

app = FastAPI()

# Настройка ресурса с указанием имени сервиса
resource = Resource.create(attributes={"service.name": "transaction_service"})

# Инициализация трейсера с ресурсом
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)

# Настройка Jaeger Exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger',  # Jaeger host из docker-compose
    agent_port=6831,           # порт Jaeger для UDP
)

# Создание процессора для отправки трейсингов в Jaeger
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Инструментирование FastAPI
FastAPIInstrumentor.instrument_app(app)

# Инструментирование HTTP-клиентов (например, requests)
RequestsInstrumentor().instrument()

# Завершение работы (shutdown) при завершении приложения
@app.on_event("shutdown")
def shutdown_tracer():
    try:
        trace.get_tracer_provider().shutdown()
    except Exception as e:
        print(f"Ошибка завершения трейсера: {e}")


@app.get('/')
def read_main():
    """Функция с приветственным текстом."""
    return {'message': 'Welcome to the Transaction Service API'}


app.include_router(router, prefix='/transaction', tags=['transaction'])
