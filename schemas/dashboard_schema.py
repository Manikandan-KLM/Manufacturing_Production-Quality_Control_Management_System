from pydantic import BaseModel


class ProductionSummary(BaseModel):
    total_orders: int
    active_orders: int
    completed_orders: int
    daily_production: float
    monthly_production: float
    production_efficiency: float


class MachineSummary(BaseModel):
    machine_utilization: float
    machine_downtime: float


class QualitySummary(BaseModel):
    rejection_rate: float
    quality_pass_percentage: float


class MaterialSummary(BaseModel):
    material_consumption: float
    low_stock_materials: int


class MaintenanceSummary(BaseModel):
    maintenance_due: int


class DefectSummary(BaseModel):
    total_defects: int
    open_defects: int
    resolved_defects: int
    critical_defects: int


class ManufacturingDashboardResponse(BaseModel):
    production: ProductionSummary
    machines: MachineSummary
    quality: QualitySummary
    materials: MaterialSummary
    maintenance: MaintenanceSummary
    defects: DefectSummary