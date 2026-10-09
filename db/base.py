from models.user_model import User
from models.revoked_token_model import RevokedToken
from models.plant_model import Plant
from models.production_line_model import ProductionLine
from models.product_model import Product
from models.material_model import Material
from models.material_history_model import MaterialHistory
from models.bom_model import BOM
from models.bom_item_model import BOMItem
from models.machine_model import Machine
from models.production_order_model import ProductionOrder
from models.production_batch_model import ProductionBatch
from models.worker_model import Worker
from models.worker_batch_assignment_model import WorkerBatchAssignment
from models.shift_model import Shift
from models.shift_worker_model import ShiftWorker
from models.shift_machine_usage_model import ShiftMachineUsage
from models.shift_production_output_model import ShiftProductionOutput
from models.quality_inspection_model import QualityInspection
from models.quality_parameter_model import QualityParameter
from models.defect_model import Defect
from models.maintenance_schedule_model import MaintenanceSchedule
from models.maintenance_model import Maintenance
from models.maintenance_spare_part_model import MaintenanceSparePart
from models.maintenance_alert_model import MaintenanceAlert
from models.downtime_model import Downtime
from models.inventory_movement_model import InventoryMovement
from models.product_inventory_model import ProductInventory
from models.production_workflow_model import ProductionWorkflowHistory
from models.audit_log_model import AuditLog
from models.mixins_model import SoftDeleteMixin


from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass