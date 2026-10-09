from datetime import date

from pydantic import BaseModel, Field


class ReportFilters:

    start_date: date | None
    end_date: date | None

    plant_id: int | None
    product_id: int | None
    machine_id: int | None
    production_line_id: int | None

    status: str | None

    search: str | None

    page: int
    page_size: int

    sort_by: str
    sort_order: str