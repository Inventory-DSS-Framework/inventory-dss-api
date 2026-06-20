from pydantic import BaseModel
from app.shared.presentation.schemas import PlaceholderResponse

class InventoryMovementRequest(BaseModel):
    pass

class BulkInventoryMovementRequest(BaseModel):
    pass

class InventoryMovementResponse(PlaceholderResponse):
    pass

class CurrentStockResponse(PlaceholderResponse):
    pass

class StockSnapshotRequest(BaseModel):
    pass

class StockSnapshotResponse(PlaceholderResponse):
    pass

class ReplenishmentRequest(BaseModel):
    pass

class ReplenishmentResponse(PlaceholderResponse):
    pass

class StockoutEventRequest(BaseModel):
    pass

class StockoutEventResponse(PlaceholderResponse):
    pass
