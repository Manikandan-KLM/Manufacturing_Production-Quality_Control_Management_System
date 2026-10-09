from sqlalchemy.orm import Session

from models.maintenance_model import Maintenance
from models.maintenance_schedule_model import MaintenanceSchedule
from models.maintenance_spare_part_model import MaintenanceSparePart
from models.maintenance_alert_model import MaintenanceAlert


class MaintenanceRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # SCHEDULE
    # -----------------------------

    def create_schedule(
        self,
        schedule: MaintenanceSchedule
    ):
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    def get_schedule_by_id(
        self,
        schedule_id: int
    ):
        return (
            self.db.query(MaintenanceSchedule)
            .filter(
                MaintenanceSchedule.id == schedule_id
            )
            .first()
        )

    def get_schedule_by_code(
        self,
        schedule_code: str
    ):
        return (
            self.db.query(MaintenanceSchedule)
            .filter(
                MaintenanceSchedule.schedule_code
                == schedule_code
            )
            .first()
        )

    def get_schedules(self):
        return (
            self.db.query(MaintenanceSchedule)
            .order_by(
                MaintenanceSchedule.next_due_date.asc()
            )
            .all()
        )

    def update_schedule(
        self,
        schedule: MaintenanceSchedule
    ):
        self.db.commit()
        self.db.refresh(schedule)

        return schedule

    # -----------------------------
    # MAINTENANCE
    # -----------------------------

    def create_maintenance(
        self,
        maintenance: Maintenance
    ):
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)

        return maintenance

    def get_maintenance_by_id(
        self,
        maintenance_id: int
    ):
        return (
            self.db.query(Maintenance)
            .filter(
                Maintenance.id == maintenance_id
            )
            .first()
        )

    def get_maintenance_by_number(
        self,
        maintenance_number: str
    ):
        return (
            self.db.query(Maintenance)
            .filter(
                Maintenance.maintenance_number
                == maintenance_number
            )
            .first()
        )

    def get_maintenance_history(
        self,
        machine_id: int | None = None
    ):
        query = self.db.query(Maintenance)

        if machine_id:
            query = query.filter(
                Maintenance.machine_id == machine_id
            )

        return (
            query
            .order_by(Maintenance.id.desc())
            .all()
        )

    def update_maintenance(
        self,
        maintenance: Maintenance
    ):
        self.db.commit()
        self.db.refresh(maintenance)

        return maintenance

    # -----------------------------
    # SPARE PARTS
    # -----------------------------

    def create_spare_part(
        self,
        spare_part: MaintenanceSparePart
    ):
        self.db.add(spare_part)
        self.db.commit()
        self.db.refresh(spare_part)

        return spare_part

    def get_spare_parts(
        self,
        maintenance_id: int
    ):
        return (
            self.db.query(MaintenanceSparePart)
            .filter(
                MaintenanceSparePart.maintenance_id
                == maintenance_id
            )
            .all()
        )

    # -----------------------------
    # ALERTS
    # -----------------------------

    def create_alert(
        self,
        alert: MaintenanceAlert
    ):
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert

    def get_alerts(
        self,
        unread_only: bool = False
    ):
        query = self.db.query(MaintenanceAlert)

        if unread_only:
            query = query.filter(
                MaintenanceAlert.is_read == False
            )

        return (
            query
            .order_by(MaintenanceAlert.id.desc())
            .all()
        )

    def get_alert_by_schedule(
        self,
        schedule_id: int
    ):
        return (
            self.db.query(MaintenanceAlert)
            .filter(
                MaintenanceAlert.schedule_id
                == schedule_id,
                MaintenanceAlert.is_read == False
            )
            .first()
        )

    def mark_alert_read(
        self,
        alert: MaintenanceAlert
    ):
        alert.is_read = True

        self.db.commit()
        self.db.refresh(alert)

        return alert