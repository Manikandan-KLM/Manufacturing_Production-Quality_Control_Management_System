from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.production_order_model import ProductionOrder
from models.production_batch_model import ProductionBatch
from models.machine_model import Machine
from models.material_model import Material
from models.quality_inspection_model import QualityInspection
from models.defect_model import Defect
from models.inventory_movement_model import InventoryMovement


class DashboardRepository:

    # =====================================================
    # PRODUCTION ORDERS
    # =====================================================

    @staticmethod
    def get_total_orders(db: Session):

        return (
            db.query(
                func.count(ProductionOrder.id)
            )
            .scalar()
            or 0
        )

    @staticmethod
    def get_active_orders(db: Session):

        active_statuses = [
            "Pending Supervisor Review",
            "Supervisor Approved",
            "Material Checked",
            "In Production",
            "Quality Approved",
            "Completed"
        ]

        return (
            db.query(
                func.count(ProductionOrder.id)
            )
            .filter(
                ProductionOrder.status.in_(active_statuses)
            )
            .scalar()
            or 0
        )

    @staticmethod
    def get_completed_orders(db: Session):

        return (
            db.query(
                func.count(ProductionOrder.id)
            )
            .filter(
                ProductionOrder.status.in_([
                    "Completed",
                    "Manager Approved"
                ])
            )
            .scalar()
            or 0
        )

    # =====================================================
    # DAILY PRODUCTION
    # =====================================================

    @staticmethod
    def get_daily_production(db: Session):

        today = date.today()

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0
                )
            )
            .filter(
                func.date(
                    ProductionBatch.start_time
                ) == today
            )
            .scalar()
        )

        return float(result or 0)

    # =====================================================
    # MONTHLY PRODUCTION
    # =====================================================

    @staticmethod
    def get_monthly_production(db: Session):

        today = date.today()

        first_day = today.replace(day=1)

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0
                )
            )
            .filter(
                ProductionBatch.start_time >= first_day
            )
            .scalar()
        )

        return float(result or 0)

    # =====================================================
    # PRODUCTION EFFICIENCY
    # =====================================================

    @staticmethod
    def get_production_efficiency(db: Session):

        planned = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.planned_quantity
                    ),
                    0
                )
            )
            .scalar()
            or 0
        )

        produced = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0
                )
            )
            .scalar()
            or 0
        )

        if planned == 0:
            return 0.0

        return round(
            (produced / planned) * 100,
            2
        )

    # =====================================================
    # MACHINE UTILIZATION
    # =====================================================

    @staticmethod
    def get_machine_utilization(db: Session):

        total_machines = (
            db.query(
                func.count(Machine.id)
            )
            .filter(
                Machine.status != "Decommissioned"
            )
            .scalar()
            or 0
        )

        running_machines = (
            db.query(
                func.count(Machine.id)
            )
            .filter(
                Machine.status == "Running"
            )
            .scalar()
            or 0
        )

        if total_machines == 0:
            return 0.0

        return round(
            (running_machines / total_machines) * 100,
            2
        )

    # =====================================================
    # MACHINE DOWNTIME
    # =====================================================

    @staticmethod
    def get_machine_downtime(db: Session):

        try:

            from models.downtime_model import Downtime

            result = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Downtime.duration_minutes
                        ),
                        0
                    )
                )
                .scalar()
            )

            return float(result or 0)

        except ImportError:

            return 0.0

    # =====================================================
    # REJECTION RATE
    # =====================================================

    @staticmethod
    def get_rejection_rate(db: Session):

        produced = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.produced_quantity
                    ),
                    0
                )
            )
            .scalar()
            or 0
        )

        rejected = (
            db.query(
                func.coalesce(
                    func.sum(
                        ProductionBatch.rejected_quantity
                    ),
                    0
                )
            )
            .scalar()
            or 0
        )

        total = produced + rejected

        if total == 0:
            return 0.0

        return round(
            (rejected / total) * 100,
            2
        )

    # =====================================================
    # QUALITY PASS %
    # =====================================================

    @staticmethod
    def get_quality_pass_percentage(db: Session):

        total = (
            db.query(
                func.count(
                    QualityInspection.id
                )
            )
            .filter(
                QualityInspection.overall_result != "Pending"
            )
            .scalar()
            or 0
        )

        passed = (
            db.query(
                func.count(
                    QualityInspection.id
                )
            )
            .filter(
                QualityInspection.overall_result == "Pass"
            )
            .scalar()
            or 0
        )

        if total == 0:
            return 0.0

        return round(
            (passed / total) * 100,
            2
        )

    # =====================================================
    # MATERIAL CONSUMPTION
    # =====================================================

    @staticmethod
    def get_material_consumption(db: Session):

        result = (
            db.query(
                func.coalesce(
                    func.sum(
                        InventoryMovement.quantity
                    ),
                    0
                )
            )
            .filter(
                InventoryMovement.movement_type
                == "Material Consumption"
            )
            .scalar()
        )

        return float(result or 0)

    # =====================================================
    # LOW STOCK MATERIALS
    # =====================================================

    @staticmethod
    def get_low_stock_materials(db: Session):

        return (
            db.query(
                func.count(Material.id)
            )
            .filter(
                Material.available_quantity
                <= Material.reorder_level
            )
            .filter(
                Material.status == "Active"
            )
            .scalar()
            or 0
        )

    # =====================================================
    # MAINTENANCE DUE
    # =====================================================

    @staticmethod
    def get_maintenance_due(db: Session):

        try:

            from models.maintenance_model import Maintenance

            result = (
                db.query(
                    func.count(Maintenance.id)
                )
                .filter(
                    Maintenance.status.in_([
                        "Scheduled",
                        "Due",
                        "Overdue"
                    ])
                )
                .scalar()
                or 0
            )

            return result

        except ImportError:

            return 0

    # =====================================================
    # DEFECT STATISTICS
    # =====================================================

    @staticmethod
    def get_defect_statistics(db: Session):

        total = (
            db.query(
                func.count(Defect.id)
            )
            .scalar()
            or 0
        )

        open_defects = (
            db.query(
                func.count(Defect.id)
            )
            .filter(
                Defect.resolution_status == "Open"
            )
            .scalar()
            or 0
        )

        resolved_defects = (
            db.query(
                func.count(Defect.id)
            )
            .filter(
                Defect.resolution_status == "Resolved"
            )
            .scalar()
            or 0
        )

        critical_defects = (
            db.query(
                func.count(Defect.id)
            )
            .filter(
                Defect.severity == "Critical"
            )
            .scalar()
            or 0
        )

        return {
            "total_defects": total,
            "open_defects": open_defects,
            "resolved_defects": resolved_defects,
            "critical_defects": critical_defects
        }