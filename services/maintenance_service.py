from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.maintenance_model import Maintenance
from models.maintenance_schedule_model import MaintenanceSchedule
from models.maintenance_spare_part_model import MaintenanceSparePart
from models.maintenance_alert_model import MaintenanceAlert

from models.machine_model import Machine
from models.material_model import Material
from models.user_model import User

from repositories.maintenance_repository import (
    MaintenanceRepository
)


class MaintenanceService:

    ALLOWED_TYPES = {
        "Preventive",
        "Breakdown"
    }

    ALLOWED_SCHEDULE_STATUS = {
        "Active",
        "Inactive",
        "Completed"
    }

    ALLOWED_STATUS = {
        "Scheduled",
        "In Progress",
        "Completed",
        "Cancelled"
    }

    def __init__(self, db: Session):

        self.db = db

        self.repository = MaintenanceRepository(db)

    # =====================================================
    # MACHINE
    # =====================================================

    def get_machine(
        self,
        machine_id: int
    ):

        machine = (
            self.db.query(Machine)
            .filter(
                Machine.id == machine_id
            )
            .first()
        )

        if not machine:

            raise HTTPException(
                status_code=404,
                detail="Machine not found"
            )

        return machine

    # =====================================================
    # TECHNICIAN
    # =====================================================

    def get_technician(
        self,
        technician_id: int
    ):

        technician = (
            self.db.query(User)
            .filter(
                User.id == technician_id
            )
            .first()
        )

        if not technician:

            raise HTTPException(
                status_code=404,
                detail="Technician not found"
            )

        if technician.role != "Maintenance Engineer":

            raise HTTPException(
                status_code=400,
                detail="Assigned user must be a Maintenance Engineer"
            )

        if not technician.is_active:

            raise HTTPException(
                status_code=400,
                detail="Maintenance Engineer is inactive"
            )

        return technician

    # =====================================================
    # CREATE SCHEDULE
    # =====================================================

    def create_schedule(
        self,
        data
    ):

        if data.maintenance_type not in self.ALLOWED_TYPES:

            raise HTTPException(
                status_code=400,
                detail="Invalid maintenance type"
            )

        if data.next_due_date < date.today():

            raise HTTPException(
                status_code=400,
                detail="Next due date cannot be in the past"
            )

        machine = self.get_machine(
            data.machine_id
        )

        if machine.status == "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail="Cannot create maintenance schedule for decommissioned machine"
            )

        existing = self.repository.get_schedule_by_code(
            data.schedule_code
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Schedule code already exists"
            )

        if (
            data.maintenance_type == "Preventive"
            and not data.frequency_days
        ):

            raise HTTPException(
                status_code=400,
                detail="Frequency days required for preventive maintenance"
            )

        schedule = MaintenanceSchedule(
            schedule_code=data.schedule_code,
            machine_id=data.machine_id,
            maintenance_type=data.maintenance_type,
            frequency_days=data.frequency_days,
            last_maintenance_date=data.last_maintenance_date,
            next_due_date=data.next_due_date,
            status="Active"
        )

        return self.repository.create_schedule(
            schedule
        )

    # =====================================================
    # UPDATE SCHEDULE
    # =====================================================

    def update_schedule(
        self,
        schedule_id: int,
        data
    ):

        schedule = self.repository.get_schedule_by_id(
            schedule_id
        )

        if not schedule:

            raise HTTPException(
                status_code=404,
                detail="Maintenance schedule not found"
            )

        if data.maintenance_type is not None:

            if data.maintenance_type not in self.ALLOWED_TYPES:

                raise HTTPException(
                    status_code=400,
                    detail="Invalid maintenance type"
                )

            schedule.maintenance_type = data.maintenance_type

        if data.frequency_days is not None:

            schedule.frequency_days = data.frequency_days

        if data.last_maintenance_date is not None:

            schedule.last_maintenance_date = (
                data.last_maintenance_date
            )

        if data.next_due_date is not None:

            if data.next_due_date < date.today():

                raise HTTPException(
                    status_code=400,
                    detail="Next due date cannot be in the past"
                )

            schedule.next_due_date = (
                data.next_due_date
            )

        return self.repository.update_schedule(
            schedule
        )

    # =====================================================
    # SCHEDULE STATUS
    # =====================================================

    def update_schedule_status(
        self,
        schedule_id: int,
        new_status: str
    ):

        if new_status not in self.ALLOWED_SCHEDULE_STATUS:

            raise HTTPException(
                status_code=400,
                detail="Invalid schedule status"
            )

        schedule = self.repository.get_schedule_by_id(
            schedule_id
        )

        if not schedule:

            raise HTTPException(
                status_code=404,
                detail="Maintenance schedule not found"
            )

        schedule.status = new_status

        return self.repository.update_schedule(
            schedule
        )

    # =====================================================
    # CREATE MAINTENANCE
    # =====================================================

    def create_maintenance(
        self,
        data
    ):

        if data.maintenance_type not in self.ALLOWED_TYPES:

            raise HTTPException(
                status_code=400,
                detail="Invalid maintenance type"
            )

        machine = self.get_machine(
            data.machine_id
        )

        if machine.status == "Decommissioned":

            raise HTTPException(
                status_code=400,
                detail="Cannot create maintenance for decommissioned machine"
            )

        existing = self.repository.get_maintenance_by_number(
            data.maintenance_number
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Maintenance number already exists"
            )

        if data.technician_id:

            self.get_technician(
                data.technician_id
            )

        maintenance = Maintenance(
            maintenance_number=data.maintenance_number,
            machine_id=data.machine_id,
            maintenance_type=data.maintenance_type,
            maintenance_date=data.maintenance_date,
            description=data.description,
            technician_id=data.technician_id,
            labor_cost=data.labor_cost,
            spare_parts_cost=0,
            total_cost=data.labor_cost,
            status="Scheduled",
            remarks=data.remarks
        )

        return self.repository.create_maintenance(
            maintenance
        )

    # =====================================================
    # UPDATE MAINTENANCE
    # =====================================================

    def update_maintenance(
        self,
        maintenance_id: int,
        data
    ):

        maintenance = (
            self.repository
            .get_maintenance_by_id(
                maintenance_id
            )
        )

        if not maintenance:

            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found"
            )

        if maintenance.status == "Completed":

            raise HTTPException(
                status_code=400,
                detail="Completed maintenance cannot be modified"
            )

        if data.description is not None:

            maintenance.description = data.description

        if data.technician_id is not None:

            self.get_technician(
                data.technician_id
            )

            maintenance.technician_id = (
                data.technician_id
            )

        if data.labor_cost is not None:

            maintenance.labor_cost = data.labor_cost

        if data.remarks is not None:

            maintenance.remarks = data.remarks

        maintenance.total_cost = (
            maintenance.labor_cost
            + maintenance.spare_parts_cost
        )

        return self.repository.update_maintenance(
            maintenance
        )

    # =====================================================
    # STATUS
    # =====================================================

    def update_maintenance_status(
        self,
        maintenance_id: int,
        new_status: str
    ):

        if new_status not in self.ALLOWED_STATUS:

            raise HTTPException(
                status_code=400,
                detail="Invalid maintenance status"
            )

        maintenance = (
            self.repository
            .get_maintenance_by_id(
                maintenance_id
            )
        )

        if not maintenance:

            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found"
            )

        allowed_transitions = {

            "Scheduled": {
                "In Progress",
                "Cancelled"
            },

            "In Progress": {
                "Completed",
                "Cancelled"
            },

            "Completed": set(),

            "Cancelled": set()
        }

        if new_status not in allowed_transitions[
            maintenance.status
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid transition from "
                    f"{maintenance.status} to "
                    f"{new_status}"
                )
            )

        maintenance.status = new_status

        if new_status == "Completed":

            maintenance.completed_at = datetime.utcnow()

            machine = self.get_machine(
                maintenance.machine_id
            )

            if machine.status == "Maintenance":

                machine.status = "Idle"

        return self.repository.update_maintenance(
            maintenance
        )

    # =====================================================
    # ADD SPARE PART
    # =====================================================

    def add_spare_part(
        self,
        maintenance_id: int,
        data
    ):

        maintenance = (
            self.repository
            .get_maintenance_by_id(
                maintenance_id
            )
        )

        if not maintenance:

            raise HTTPException(
                status_code=404,
                detail="Maintenance record not found"
            )

        if maintenance.status == "Completed":

            raise HTTPException(
                status_code=400,
                detail="Cannot add spare parts to completed maintenance"
            )

        material = (
            self.db.query(Material)
            .filter(
                Material.id == data.material_id
            )
            .first()
        )

        if not material:

            raise HTTPException(
                status_code=404,
                detail="Material not found"
            )

        if material.status != "Active":

            raise HTTPException(
                status_code=400,
                detail="Material is inactive"
            )

        if material.available_quantity < data.quantity_used:

            raise HTTPException(
                status_code=400,
                detail="Insufficient material stock"
            )

        total_cost = (
            data.quantity_used
            * data.unit_cost
        )

        spare_part = MaintenanceSparePart(
            maintenance_id=maintenance_id,
            material_id=data.material_id,
            quantity_used=data.quantity_used,
            unit_cost=data.unit_cost,
            total_cost=total_cost
        )

        # Reduce inventory
        material.available_quantity -= (
            data.quantity_used
        )

        maintenance.spare_parts_cost += total_cost

        maintenance.total_cost = (
            maintenance.labor_cost
            + maintenance.spare_parts_cost
        )

        self.db.add(spare_part)

        self.db.commit()

        self.db.refresh(spare_part)

        return spare_part

    # =====================================================
    # MAINTENANCE HISTORY
    # =====================================================

    def get_history(
        self,
        machine_id: int | None = None
    ):

        return self.repository.get_maintenance_history(
            machine_id
        )

    # =====================================================
    # DUE ALERTS
    # =====================================================

    def generate_due_alerts(self):

        schedules = self.repository.get_schedules()

        today = date.today()

        generated_alerts = []

        for schedule in schedules:

            if schedule.status != "Active":
                continue

            if schedule.next_due_date <= today:

                existing = (
                    self.repository
                    .get_alert_by_schedule(
                        schedule.id
                    )
                )

                if existing:
                    continue

                machine = self.get_machine(
                    schedule.machine_id
                )

                alert = MaintenanceAlert(

                    machine_id=schedule.machine_id,

                    schedule_id=schedule.id,

                    alert_message=(
                        f"Maintenance due for "
                        f"machine {machine.machine_code}"
                    ),

                    due_date=datetime.combine(
                        schedule.next_due_date,
                        datetime.min.time()
                    ),

                    is_read=False
                )

                created_alert = (
                    self.repository
                    .create_alert(alert)
                )

                generated_alerts.append(
                    created_alert
                )

        return generated_alerts

    # =====================================================
    # ALERTS
    # =====================================================

    def get_alerts(
        self,
        unread_only=False
    ):

        return self.repository.get_alerts(
            unread_only
        )

    def mark_alert_read(
        self,
        alert_id: int
    ):

        alert = (
            self.db.query(MaintenanceAlert)
            .filter(
                MaintenanceAlert.id == alert_id
            )
            .first()
        )

        if not alert:

            raise HTTPException(
                status_code=404,
                detail="Maintenance alert not found"
            )

        return self.repository.mark_alert_read(
            alert
        )