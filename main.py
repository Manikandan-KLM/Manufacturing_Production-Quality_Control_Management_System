from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.limiter import limiter
from core.exceptions import register_exception_handlers

from api import auth_routes
from api import plants_routes
from api import production_lines_routes
from api import products_routes
from api import materials_routes
from api import boms_routes
from api import machines_routes
from api import production_orders_routes
from api import production_batches_routes
from api import workers_routes
from api import shifts_routes
from api import quality_routes
from api import defects_routes
from api import maintenance_routes
from api import downtime_routes
from api import inventory_routes
from api import production_workflow_routes
from api import dashboard_routes
from api import report_routes
from api import audit_log_routes




app = FastAPI(title=settings.APP_NAME,version=settings.APP_VERSION)



app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

register_exception_handlers(app)


# ==========================================
# AUTH ROUTES
# ==========================================

app.include_router(auth_routes.router)
app.include_router(plants_routes.router)
app.include_router(production_lines_routes.router)
app.include_router(products_routes.router)
app.include_router(materials_routes.router)
app.include_router(boms_routes.router)
app.include_router(machines_routes.router)
app.include_router(production_orders_routes.router)
app.include_router(production_batches_routes.router)
app.include_router(workers_routes.router)
app.include_router(shifts_routes.router)
app.include_router(quality_routes.router)
app.include_router(defects_routes.router)
app.include_router(maintenance_routes.router)
app.include_router(downtime_routes.router)
app.include_router(inventory_routes.router)
app.include_router(production_workflow_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(report_routes.router)
app.include_router(audit_log_routes.router)



@app.get("/")
def root():

    return {
        "message": "Manufacturing Management System API is running"
    }






