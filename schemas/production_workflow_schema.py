from pydantic import BaseModel, Field


class WorkflowActionRequest(BaseModel):
    remarks: str | None = Field(
        default=None,
        max_length=500
    )


class WorkflowHistoryResponse(BaseModel):
    id: int
    production_order_id: int
    from_status: str | None
    to_status: str
    action: str
    remarks: str | None
    performed_by: int
    created_at: str

    class Config:
        from_attributes = True


class ProductionWorkflowResponse(BaseModel):
    production_order_id: int
    order_number: str
    status: str