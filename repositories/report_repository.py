from datetime import date, datetime, timedelta

from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

from models.production_batch_model import ProductionBatch
from models.production_order_model import ProductionOrder
from models.product_model import Product
from models.production_line_model import ProductionLine
from models.plant_model import Plant
from models.machine_model import Machine
from models.quality_inspection_model import QualityInspection
from models.defect_model import Defect
from models.material_model import Material
from models.inventory_movement_model import InventoryMovement
from models.worker_model import Worker
from models.worker_batch_assignment_model import WorkerBatchAssignment
from models.shift_model import Shift
from models.shift_production_output_model import ShiftProductionOutput
from models.downtime_model import Downtime


class ReportRepository:

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # COMMON DATE FILTER
    # =========================================================

    @staticmethod
    def apply_date_filter(
        query,
        column,
        start_date: date | None,
        end_date: date | None,
    ):
        if start_date:
            query = query.filter(
                column >= datetime.combine(start_date, datetime.min.time())
            )

        if end_date:
            next_day = end_date + timedelta(days=1)

            query = query.filter(
                column < datetime.combine(next_day, datetime.min.time())
            )

        return query

    # =========================================================
    # 1. DAILY PRODUCTION REPORT
    # =========================================================

    def daily_production_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        status=None,
        search=None,
    ):
        production_date = func.date(ProductionBatch.start_time)

        query = (
            self.db.query(
                production_date.label("production_date"),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                Product.id.label("product_id"),
                Product.product_name.label("product_name"),
                ProductionLine.id.label("production_line_id"),
                ProductionLine.line_name.label("production_line_name"),
                func.sum(
                    ProductionBatch.planned_quantity
                ).label("planned_quantity"),
                func.sum(
                    ProductionBatch.produced_quantity
                ).label("produced_quantity"),
                func.sum(
                    ProductionBatch.rejected_quantity
                ).label("rejected_quantity"),
            )
            .join(
                ProductionOrder,
                ProductionBatch.production_order_id
                == ProductionOrder.id,
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.id,
            )
            .join(
                ProductionLine,
                ProductionBatch.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            ProductionBatch.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if status:
            query = query.filter(
                ProductionOrder.status == status
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Product.product_name.ilike(search_value)
                | Product.product_code.ilike(search_value)
                | ProductionLine.line_name.ilike(search_value)
            )

        query = query.group_by(
            production_date,
            Plant.id,
            Plant.plant_name,
            Product.id,
            Product.product_name,
            ProductionLine.id,
            ProductionLine.line_name,
        )

        return query

    # =========================================================
    # 2. MONTHLY PRODUCTION REPORT
    # =========================================================

    def monthly_production_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        status=None,
        search=None,
    ):
        year_value = func.extract(
            "year",
            ProductionBatch.start_time,
        )

        month_value = func.extract(
            "month",
            ProductionBatch.start_time,
        )

        query = (
            self.db.query(
                year_value.label("year"),
                month_value.label("month"),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                Product.id.label("product_id"),
                Product.product_name.label("product_name"),
                func.sum(
                    ProductionBatch.planned_quantity
                ).label("planned_quantity"),
                func.sum(
                    ProductionBatch.produced_quantity
                ).label("produced_quantity"),
                func.sum(
                    ProductionBatch.rejected_quantity
                ).label("rejected_quantity"),
            )
            .join(
                ProductionOrder,
                ProductionBatch.production_order_id
                == ProductionOrder.id,
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.id,
            )
            .join(
                ProductionLine,
                ProductionBatch.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            ProductionBatch.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if status:
            query = query.filter(
                ProductionOrder.status == status
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Product.product_name.ilike(search_value)
                | Product.product_code.ilike(search_value)
            )

        query = query.group_by(
            year_value,
            month_value,
            Plant.id,
            Plant.plant_name,
            Product.id,
            Product.product_name,
        )

        return query

    # =========================================================
    # 3. MACHINE PERFORMANCE REPORT
    # =========================================================

    def machine_performance_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        machine_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Machine.id.label("machine_id"),
                Machine.machine_code.label("machine_code"),
                Machine.machine_name.label("machine_name"),
                Machine.status.label("machine_status"),
                ProductionLine.id.label("production_line_id"),
                ProductionLine.line_name.label(
                    "production_line_name"
                ),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                func.count(
                    ProductionBatch.id
                ).label("batch_count"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.planned_quantity
                    ),
                    0,
                ).label("planned_quantity"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0,
                ).label("produced_quantity"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.rejected_quantity
                    ),
                    0,
                ).label("rejected_quantity"),
            )
            .join(
                ProductionBatch,
                ProductionBatch.machine_id == Machine.id,
            )
            .join(
                ProductionLine,
                Machine.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            ProductionBatch.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if machine_id:
            query = query.filter(
                Machine.id == machine_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Machine.machine_name.ilike(search_value)
                | Machine.machine_code.ilike(search_value)
            )

        query = query.group_by(
            Machine.id,
            Machine.machine_code,
            Machine.machine_name,
            Machine.status,
            ProductionLine.id,
            ProductionLine.line_name,
            Plant.id,
            Plant.plant_name,
        )

        return query

    # =========================================================
    # 4. PRODUCT-WISE PRODUCTION REPORT
    # =========================================================

    def product_production_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        status=None,
        search=None,
    ):
        query = (
            self.db.query(
                Product.id.label("product_id"),
                Product.product_code.label("product_code"),
                Product.product_name.label("product_name"),
                Product.category.label("category"),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                func.count(
                    ProductionBatch.id
                ).label("batch_count"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.planned_quantity
                    ),
                    0,
                ).label("planned_quantity"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0,
                ).label("produced_quantity"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.rejected_quantity
                    ),
                    0,
                ).label("rejected_quantity"),
            )
            .join(
                ProductionOrder,
                ProductionBatch.production_order_id
                == ProductionOrder.id,
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.id,
            )
            .join(
                ProductionLine,
                ProductionBatch.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            ProductionBatch.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if status:
            query = query.filter(
                ProductionOrder.status == status
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Product.product_name.ilike(search_value)
                | Product.product_code.ilike(search_value)
                | Product.category.ilike(search_value)
            )

        query = query.group_by(
            Product.id,
            Product.product_code,
            Product.product_name,
            Product.category,
            Plant.id,
            Plant.plant_name,
        )

        return query

    # =========================================================
    # 5. QUALITY REPORT
    # =========================================================

    def quality_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Product.id.label("product_id"),
                Product.product_name.label("product_name"),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                func.count(
                    QualityInspection.id
                ).label("total_inspections"),
                func.sum(
                    func.cast(
                        QualityInspection.overall_result == "Pass",
                        Integer,
                    )
                ).label("passed_inspections"),
                func.sum(
                    func.cast(
                        QualityInspection.overall_result == "Fail",
                        Integer,
                    )
                ).label("failed_inspections"),
            )
            .join(
                ProductionBatch,
                QualityInspection.production_batch_id
                == ProductionBatch.id,
            )
            .join(
                ProductionOrder,
                ProductionBatch.production_order_id
                == ProductionOrder.id,
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.id,
            )
            .join(
                ProductionLine,
                ProductionBatch.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            QualityInspection.inspection_date,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Product.product_name.ilike(search_value)
                | Product.product_code.ilike(search_value)
            )

        query = query.group_by(
            Product.id,
            Product.product_name,
            Plant.id,
            Plant.plant_name,
        )

        return query

    # =========================================================
    # 6. DEFECT ANALYSIS
    # =========================================================

    def defect_analysis(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        status=None,
        search=None,
    ):
        query = (
            self.db.query(
                Defect.defect_type.label("defect_type"),
                Defect.severity.label("severity"),
                Defect.resolution_status.label(
                    "resolution_status"
                ),
                Product.id.label("product_id"),
                Product.product_name.label("product_name"),
                func.count(
                    Defect.id
                ).label("defect_count"),
                func.coalesce(
                    func.sum(
                        Defect.quantity_affected
                    ),
                    0,
                ).label("quantity_affected"),
            )
            .join(
                ProductionBatch,
                Defect.production_batch_id
                == ProductionBatch.id,
            )
            .join(
                ProductionOrder,
                ProductionBatch.production_order_id
                == ProductionOrder.id,
            )
            .join(
                Product,
                ProductionOrder.product_id == Product.id,
            )
            .join(
                ProductionLine,
                ProductionBatch.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            Defect.created_at,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if status:
            query = query.filter(
                Defect.resolution_status == status
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Defect.defect_type.ilike(search_value)
                | Product.product_name.ilike(search_value)
            )

        query = query.group_by(
            Defect.defect_type,
            Defect.severity,
            Defect.resolution_status,
            Product.id,
            Product.product_name,
        )

        return query

    # =========================================================
    # 7. MATERIAL CONSUMPTION REPORT
    # =========================================================

    def material_consumption_report(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        product_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Material.id.label("material_id"),
                Material.material_code.label("material_code"),
                Material.material_name.label("material_name"),
                Material.unit_of_measurement.label(
                    "unit_of_measurement"
                ),
                func.count(
                    InventoryMovement.id
                ).label("transaction_count"),
                func.coalesce(
                    func.sum(
                        InventoryMovement.quantity
                    ),
                    0,
                ).label("consumed_quantity"),
            )
            .join(
                InventoryMovement,
                InventoryMovement.material_id
                == Material.id,
            )
        )

        # Material consumption related to production batch
        query = query.outerjoin(
            ProductionBatch,
            InventoryMovement.production_batch_id
            == ProductionBatch.id,
        )

        query = query.outerjoin(
            ProductionOrder,
            ProductionBatch.production_order_id
            == ProductionOrder.id,
        )

        query = query.outerjoin(
            Product,
            ProductionOrder.product_id == Product.id,
        )

        query = query.outerjoin(
            ProductionLine,
            ProductionBatch.production_line_id
            == ProductionLine.id,
        )

        query = query.outerjoin(
            Plant,
            ProductionLine.plant_id == Plant.id,
        )

        query = query.filter(
            InventoryMovement.movement_type
            == "Material Consumption"
        )

        query = self.apply_date_filter(
            query,
            InventoryMovement.created_at,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if product_id:
            query = query.filter(
                Product.id == product_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Material.material_name.ilike(search_value)
                | Material.material_code.ilike(search_value)
            )

        query = query.group_by(
            Material.id,
            Material.material_code,
            Material.material_name,
            Material.unit_of_measurement,
        )

        return query

    # =========================================================
    # 8. WORKER PERFORMANCE REPORT
    # =========================================================

    def worker_performance(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Worker.id.label("worker_id"),
                Worker.employee_code.label("employee_code"),
                Worker.full_name.label("worker_name"),
                Worker.department.label("department"),
                ProductionLine.id.label("production_line_id"),
                ProductionLine.line_name.label(
                    "production_line_name"
                ),
                func.count(
                    ProductionBatch.id
                ).label("batch_count"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0,
                ).label("produced_quantity"),
                func.coalesce(
                    func.sum(
                        ProductionBatch.rejected_quantity
                    ),
                    0,
                ).label("rejected_quantity"),
            )
            .join(
                WorkerBatchAssignment,
                Worker.id == WorkerBatchAssignment.worker_id,
            )
            .join(
                ProductionBatch,
                WorkerBatchAssignment.production_batch_id
                == ProductionBatch.id,
            )
            .outerjoin(
                ProductionLine,
                Worker.production_line_id
                == ProductionLine.id,
            )
            .outerjoin(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            ProductionBatch.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Worker.full_name.ilike(search_value)
                | Worker.employee_code.ilike(search_value)
            )

        query = query.group_by(
            Worker.id,
            Worker.employee_code,
            Worker.full_name,
            Worker.department,
            ProductionLine.id,
            ProductionLine.line_name,
        )

        return query

    # =========================================================
    # 9. SHIFT PERFORMANCE REPORT
    # =========================================================

    def shift_performance(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Shift.id.label("shift_id"),
                Shift.shift_code.label("shift_code"),
                Shift.shift_name.label("shift_name"),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                func.count(
                    ShiftProductionOutput.id
                ).label("output_count"),
                func.coalesce(
                    func.sum(
                        ShiftProductionOutput.planned_quantity
                    ),
                    0,
                ).label("planned_quantity"),
                func.coalesce(
                    func.sum(
                        ShiftProductionOutput.produced_quantity
                    ),
                    0,
                ).label("produced_quantity"),
                func.coalesce(
                    func.sum(
                        ShiftProductionOutput.rejected_quantity
                    ),
                    0,
                ).label("rejected_quantity"),
            )
            .join(
                ShiftProductionOutput,
                Shift.id == ShiftProductionOutput.shift_id,
            )
            .join(
                Plant,
                Shift.plant_id == Plant.id,
            )
        )

        if start_date:
            query = query.filter(
                ShiftProductionOutput.work_date >= start_date
            )

        if end_date:
            query = query.filter(
                ShiftProductionOutput.work_date <= end_date
            )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Shift.shift_name.ilike(search_value)
                | Shift.shift_code.ilike(search_value)
            )

        query = query.group_by(
            Shift.id,
            Shift.shift_code,
            Shift.shift_name,
            Plant.id,
            Plant.plant_name,
        )

        return query

    # =========================================================
    # 10. DOWNTIME ANALYSIS
    # =========================================================

    def downtime_analysis(
        self,
        start_date=None,
        end_date=None,
        plant_id=None,
        machine_id=None,
        production_line_id=None,
        search=None,
    ):
        query = (
            self.db.query(
                Machine.id.label("machine_id"),
                Machine.machine_code.label("machine_code"),
                Machine.machine_name.label("machine_name"),
                ProductionLine.id.label("production_line_id"),
                ProductionLine.line_name.label(
                    "production_line_name"
                ),
                Plant.id.label("plant_id"),
                Plant.plant_name.label("plant_name"),
                Downtime.reason.label("reason"),
                func.count(
                    Downtime.id
                ).label("downtime_count"),
                func.coalesce(
                    func.sum(
                        Downtime.duration_minutes
                    ),
                    0,
                ).label("downtime_minutes"),
            )
            .join(
                Machine,
                Downtime.machine_id == Machine.id,
            )
            .join(
                ProductionLine,
                Machine.production_line_id
                == ProductionLine.id,
            )
            .join(
                Plant,
                ProductionLine.plant_id == Plant.id,
            )
        )

        query = self.apply_date_filter(
            query,
            Downtime.start_time,
            start_date,
            end_date,
        )

        if plant_id:
            query = query.filter(
                Plant.id == plant_id
            )

        if machine_id:
            query = query.filter(
                Machine.id == machine_id
            )

        if production_line_id:
            query = query.filter(
                ProductionLine.id == production_line_id
            )

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Machine.machine_name.ilike(search_value)
                | Machine.machine_code.ilike(search_value)
                | Downtime.reason.ilike(search_value)
            )

        query = query.group_by(
            Machine.id,
            Machine.machine_code,
            Machine.machine_name,
            ProductionLine.id,
            ProductionLine.line_name,
            Plant.id,
            Plant.plant_name,
            Downtime.reason,
        )

        return query