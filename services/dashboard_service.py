from sqlalchemy.orm import Session

from repositories.dashboard_repository import (
    DashboardRepository
)


class DashboardService:

    @staticmethod
    def get_dashboard(db: Session):

        total_orders = (
            DashboardRepository
            .get_total_orders(db)
        )

        active_orders = (
            DashboardRepository
            .get_active_orders(db)
        )

        completed_orders = (
            DashboardRepository
            .get_completed_orders(db)
        )

        daily_production = (
            DashboardRepository
            .get_daily_production(db)
        )

        monthly_production = (
            DashboardRepository
            .get_monthly_production(db)
        )

        production_efficiency = (
            DashboardRepository
            .get_production_efficiency(db)
        )

        machine_utilization = (
            DashboardRepository
            .get_machine_utilization(db)
        )

        machine_downtime = (
            DashboardRepository
            .get_machine_downtime(db)
        )

        rejection_rate = (
            DashboardRepository
            .get_rejection_rate(db)
        )

        quality_pass_percentage = (
            DashboardRepository
            .get_quality_pass_percentage(db)
        )

        material_consumption = (
            DashboardRepository
            .get_material_consumption(db)
        )

        low_stock_materials = (
            DashboardRepository
            .get_low_stock_materials(db)
        )

        maintenance_due = (
            DashboardRepository
            .get_maintenance_due(db)
        )

        defect_statistics = (
            DashboardRepository
            .get_defect_statistics(db)
        )

        return {
            "production": {
                "total_orders": total_orders,
                "active_orders": active_orders,
                "completed_orders": completed_orders,
                "daily_production": daily_production,
                "monthly_production": monthly_production,
                "production_efficiency":
                    production_efficiency
            },

            "machines": {
                "machine_utilization":
                    machine_utilization,
                "machine_downtime":
                    machine_downtime
            },

            "quality": {
                "rejection_rate":
                    rejection_rate,
                "quality_pass_percentage":
                    quality_pass_percentage
            },

            "materials": {
                "material_consumption":
                    material_consumption,
                "low_stock_materials":
                    low_stock_materials
            },

            "maintenance": {
                "maintenance_due":
                    maintenance_due
            },

            "defects": defect_statistics
        }