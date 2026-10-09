from math import ceil

from sqlalchemy.orm import Session

from repositories.report_repository import ReportRepository


class ReportService:

    def __init__(self, db: Session):
        self.repository = ReportRepository(db)

    # =========================================================
    # PAGINATION
    # =========================================================

    @staticmethod
    def paginate(
        items,
        page: int,
        page_size: int,
    ):
        total = len(items)

        start = (page - 1) * page_size
        end = start + page_size

        paginated_items = items[start:end]

        total_pages = (
            ceil(total / page_size)
            if total > 0
            else 0
        )

        return {
            "items": paginated_items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # =========================================================
    # SAFE FLOAT
    # =========================================================

    @staticmethod
    def safe_float(value):
        if value is None:
            return 0.0

        return float(value)

    # =========================================================
    # EFFICIENCY
    # =========================================================

    @staticmethod
    def calculate_efficiency(
        planned_quantity,
        produced_quantity,
    ):
        planned = ReportService.safe_float(
            planned_quantity
        )

        produced = ReportService.safe_float(
            produced_quantity
        )

        if planned <= 0:
            return 0.0

        return round(
            (produced / planned) * 100,
            2,
        )

    # =========================================================
    # REJECTION RATE
    # =========================================================

    @staticmethod
    def calculate_rejection_rate(
        produced_quantity,
        rejected_quantity,
    ):
        produced = ReportService.safe_float(
            produced_quantity
        )

        rejected = ReportService.safe_float(
            rejected_quantity
        )

        total = produced + rejected

        if total <= 0:
            return 0.0

        return round(
            (rejected / total) * 100,
            2,
        )

    # =========================================================
    # 1. DAILY PRODUCTION
    # =========================================================

    def daily_production(
        self,
        filters,
    ):
        query = self.repository.daily_production_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            status=filters.status,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            planned = self.safe_float(
                row.planned_quantity
            )

            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "production_date": row.production_date,
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "production_line_id": row.production_line_id,
                    "production_line_name": (
                        row.production_line_name
                    ),
                    "planned_quantity": planned,
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "efficiency_percentage": (
                        self.calculate_efficiency(
                            planned,
                            produced,
                        )
                    ),
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 2. MONTHLY PRODUCTION
    # =========================================================

    def monthly_production(
        self,
        filters,
    ):
        query = self.repository.monthly_production_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            status=filters.status,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            planned = self.safe_float(
                row.planned_quantity
            )

            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "planned_quantity": planned,
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "efficiency_percentage": (
                        self.calculate_efficiency(
                            planned,
                            produced,
                        )
                    ),
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 3. MACHINE PERFORMANCE
    # =========================================================

    def machine_performance(
        self,
        filters,
    ):
        query = self.repository.machine_performance_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            machine_id=filters.machine_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            planned = self.safe_float(
                row.planned_quantity
            )

            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "machine_id": row.machine_id,
                    "machine_code": row.machine_code,
                    "machine_name": row.machine_name,
                    "machine_status": row.machine_status,
                    "production_line_id": (
                        row.production_line_id
                    ),
                    "production_line_name": (
                        row.production_line_name
                    ),
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "batch_count": row.batch_count,
                    "planned_quantity": planned,
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "efficiency_percentage": (
                        self.calculate_efficiency(
                            planned,
                            produced,
                        )
                    ),
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 4. PRODUCT PRODUCTION
    # =========================================================

    def product_production(
        self,
        filters,
    ):
        query = self.repository.product_production_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            status=filters.status,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            planned = self.safe_float(
                row.planned_quantity
            )

            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "product_id": row.product_id,
                    "product_code": row.product_code,
                    "product_name": row.product_name,
                    "category": row.category,
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "batch_count": row.batch_count,
                    "planned_quantity": planned,
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "efficiency_percentage": (
                        self.calculate_efficiency(
                            planned,
                            produced,
                        )
                    ),
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 5. QUALITY REPORT
    # =========================================================

    def quality(
        self,
        filters,
    ):
        query = self.repository.quality_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            total = int(
                row.total_inspections or 0
            )

            passed = int(
                row.passed_inspections or 0
            )

            failed = int(
                row.failed_inspections or 0
            )

            if total > 0:
                pass_percentage = round(
                    (passed / total) * 100,
                    2,
                )

                fail_percentage = round(
                    (failed / total) * 100,
                    2,
                )
            else:
                pass_percentage = 0.0
                fail_percentage = 0.0

            items.append(
                {
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "total_inspections": total,
                    "passed_inspections": passed,
                    "failed_inspections": failed,
                    "pass_percentage": pass_percentage,
                    "fail_percentage": fail_percentage,
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 6. DEFECT ANALYSIS
    # =========================================================

    def defects(
        self,
        filters,
    ):
        query = self.repository.defect_analysis(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            status=filters.status,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            items.append(
                {
                    "defect_type": row.defect_type,
                    "severity": row.severity,
                    "resolution_status": (
                        row.resolution_status
                    ),
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "defect_count": int(
                        row.defect_count or 0
                    ),
                    "quantity_affected": (
                        self.safe_float(
                            row.quantity_affected
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 7. MATERIAL CONSUMPTION
    # =========================================================

    def materials(
        self,
        filters,
    ):
        query = self.repository.material_consumption_report(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            product_id=filters.product_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            items.append(
                {
                    "material_id": row.material_id,
                    "material_code": row.material_code,
                    "material_name": row.material_name,
                    "unit_of_measurement": (
                        row.unit_of_measurement
                    ),
                    "transaction_count": int(
                        row.transaction_count or 0
                    ),
                    "consumed_quantity": (
                        self.safe_float(
                            row.consumed_quantity
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 8. WORKER PERFORMANCE
    # =========================================================

    def workers(
        self,
        filters,
    ):
        query = self.repository.worker_performance(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "worker_id": row.worker_id,
                    "employee_code": row.employee_code,
                    "worker_name": row.worker_name,
                    "department": row.department,
                    "production_line_id": (
                        row.production_line_id
                    ),
                    "production_line_name": (
                        row.production_line_name
                    ),
                    "batch_count": int(
                        row.batch_count or 0
                    ),
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 9. SHIFT PERFORMANCE
    # =========================================================

    def shifts(
        self,
        filters,
    ):
        query = self.repository.shift_performance(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            planned = self.safe_float(
                row.planned_quantity
            )

            produced = self.safe_float(
                row.produced_quantity
            )

            rejected = self.safe_float(
                row.rejected_quantity
            )

            items.append(
                {
                    "shift_id": row.shift_id,
                    "shift_code": row.shift_code,
                    "shift_name": row.shift_name,
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "output_count": int(
                        row.output_count or 0
                    ),
                    "planned_quantity": planned,
                    "produced_quantity": produced,
                    "rejected_quantity": rejected,
                    "efficiency_percentage": (
                        self.calculate_efficiency(
                            planned,
                            produced,
                        )
                    ),
                    "rejection_rate_percentage": (
                        self.calculate_rejection_rate(
                            produced,
                            rejected,
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # 10. DOWNTIME ANALYSIS
    # =========================================================

    def downtime(
        self,
        filters,
    ):
        query = self.repository.downtime_analysis(
            start_date=filters.start_date,
            end_date=filters.end_date,
            plant_id=filters.plant_id,
            machine_id=filters.machine_id,
            production_line_id=filters.production_line_id,
            search=filters.search,
        )

        rows = query.all()

        items = []

        for row in rows:
            items.append(
                {
                    "machine_id": row.machine_id,
                    "machine_code": row.machine_code,
                    "machine_name": row.machine_name,
                    "production_line_id": (
                        row.production_line_id
                    ),
                    "production_line_name": (
                        row.production_line_name
                    ),
                    "plant_id": row.plant_id,
                    "plant_name": row.plant_name,
                    "reason": row.reason,
                    "downtime_count": int(
                        row.downtime_count or 0
                    ),
                    "downtime_minutes": (
                        self.safe_float(
                            row.downtime_minutes
                        )
                    ),
                }
            )

        items = self.sort_items(
            items,
            filters.sort_by,
            filters.sort_order,
        )

        return self.paginate(
            items,
            filters.page,
            filters.page_size,
        )

    # =========================================================
    # SORTING
    # =========================================================

    @staticmethod
    def sort_items(
        items,
        sort_by,
        sort_order,
    ):
        if not items:
            return items

        allowed_fields = {
            "production_date",
            "year",
            "month",
            "product_name",
            "product_code",
            "machine_name",
            "machine_code",
            "worker_name",
            "produced_quantity",
            "planned_quantity",
            "rejected_quantity",
            "efficiency_percentage",
            "rejection_rate_percentage",
            "pass_percentage",
            "fail_percentage",
            "defect_count",
            "quantity_affected",
            "consumed_quantity",
            "downtime_minutes",
            "batch_count",
            "shift_name",
        }

        if sort_by not in allowed_fields:
            return items

        reverse = sort_order == "desc"

        def sort_key(item):
            value = item.get(sort_by)

            if value is None:
                return 0

            return value

        try:
            return sorted(
                items,
                key=sort_key,
                reverse=reverse,
            )
        except TypeError:
            return items