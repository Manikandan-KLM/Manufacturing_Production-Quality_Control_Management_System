
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from services.inventory_service import InventoryService


# ==================================================
# FIXTURES
# ==================================================

@pytest.fixture
def db():
    database = MagicMock()
    database.query.return_value.filter.return_value.first.return_value = None
    return database


@pytest.fixture
def service(db):
    with patch(
        "services.inventory_service.InventoryRepository"
    ) as repo_class:
        inventory_service = InventoryService(db)
        inventory_service.repository = repo_class.return_value
        yield inventory_service


@pytest.fixture
def material():
    return SimpleNamespace(
        id=1,
        name="Steel",
        status="Active",
        available_quantity=100,
    )


@pytest.fixture
def inactive_material():
    return SimpleNamespace(
        id=2,
        name="Inactive Steel",
        status="Inactive",
        available_quantity=50,
    )


@pytest.fixture
def product():
    return SimpleNamespace(
        id=1,
        name="Laptop",
        status="Active",
    )


@pytest.fixture
def inactive_product():
    return SimpleNamespace(
        id=2,
        name="Old Laptop",
        status="Inactive",
    )


@pytest.fixture
def batch():
    return SimpleNamespace(
        id=1,
        batch_number="BATCH001",
    )


@pytest.fixture
def movement():
    return SimpleNamespace(
        id=1,
        transaction_number="TXN001",
        movement_type="Raw Material Receipt",
        material_id=1,
        product_id=None,
        production_batch_id=None,
        quantity=10,
        quantity_before=100,
        quantity_after=110,
        reference_number="REF001",
        reason="Stock received",
        performed_by=1,
    )


def make_data(**kwargs):
    defaults = {
        "transaction_number": "TXN001",
        "material_id": 1,
        "product_id": 1,
        "production_batch_id": 1,
        "quantity": 10,
        "reference_number": "REF001",
        "reason": "Test inventory transaction",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ==================================================
# DUPLICATE TRANSACTION CHECK
# ==================================================

def test_check_transaction_number_success(service):
    service.repository.get_by_transaction_number.return_value = None

    result = service.check_transaction_number("TXN001")

    assert result is None
    service.repository.get_by_transaction_number.assert_called_once_with(
        "TXN001"
    )


def test_check_transaction_number_duplicate(service, movement):
    service.repository.get_by_transaction_number.return_value = movement

    with pytest.raises(HTTPException) as exc:
        service.check_transaction_number("TXN001")

    assert exc.value.status_code == 409
    assert exc.value.detail == "Transaction number already exists"


# ==================================================
# GET MATERIAL
# ==================================================

def test_get_material_success(service, db, material):
    db.query.return_value.filter.return_value.first.return_value = material

    result = service.get_material(1)

    assert result == material


def test_get_material_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_material(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Material not found"


def test_get_material_inactive(service, db, inactive_material):
    db.query.return_value.filter.return_value.first.return_value = (
        inactive_material
    )

    with pytest.raises(HTTPException) as exc:
        service.get_material(2)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Material is inactive"


# ==================================================
# GET PRODUCT
# ==================================================

def test_get_product_success(service, db, product):
    db.query.return_value.filter.return_value.first.return_value = product

    result = service.get_product(1)

    assert result == product


def test_get_product_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_product(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"


def test_get_product_inactive(service, db, inactive_product):
    db.query.return_value.filter.return_value.first.return_value = (
        inactive_product
    )

    with pytest.raises(HTTPException) as exc:
        service.get_product(2)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Product is inactive"


# ==================================================
# GET PRODUCTION BATCH
# ==================================================

def test_get_batch_success(service, db, batch):
    db.query.return_value.filter.return_value.first.return_value = batch

    result = service.get_batch(1)

    assert result == batch


def test_get_batch_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_batch(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Production batch not found"


# ==================================================
# RECEIVE MATERIAL
# ==================================================

def test_receive_material_success(service, db, material, movement):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)

    service.db.add = MagicMock()
    service.db.commit = MagicMock()
    service.db.refresh = MagicMock()

    data = make_data(quantity=20)

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ) as movement_model:
        result = service.receive_material(data, performed_by=5)

    assert result == movement
    assert material.available_quantity == 120

    movement_model.assert_called_once_with(
        transaction_number="TXN001",
        movement_type="Raw Material Receipt",
        material_id=1,
        product_id=None,
        production_batch_id=None,
        quantity=20,
        quantity_before=100,
        quantity_after=120,
        reference_number="REF001",
        reason="Test inventory transaction",
        performed_by=5,
    )

    db.add.assert_called_once_with(movement)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(movement)




def test_receive_material_inactive_material(service):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(
        side_effect=HTTPException(
            status_code=400,
            detail="Material is inactive",
        )
    )

    with pytest.raises(HTTPException) as exc:
        service.receive_material(make_data(), performed_by=1)

    assert exc.value.status_code == 400


# ==================================================
# CONSUME MATERIAL
# ==================================================

def test_consume_material_success(service, material, batch, movement):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)
    service.get_batch = MagicMock(return_value=batch)

    service.db.add = MagicMock()
    service.db.commit = MagicMock()
    service.db.refresh = MagicMock()

    data = make_data(quantity=30)

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ):
        result = service.consume_material(data, performed_by=5)

    assert result == movement
    assert material.available_quantity == 70

    service.db.add.assert_called_once_with(movement)
    service.db.commit.assert_called_once()
    service.db.refresh.assert_called_once_with(movement)


def test_consume_material_insufficient_stock(service, material, batch):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)
    service.get_batch = MagicMock(return_value=batch)

    data = make_data(quantity=150)

    with pytest.raises(HTTPException) as exc:
        service.consume_material(data, performed_by=1)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Insufficient material stock"
    assert material.available_quantity == 100
    service.db.add.assert_not_called()
    service.db.commit.assert_not_called()


def test_consume_material_batch_not_found(service, material):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)
    service.get_batch = MagicMock(
        side_effect=HTTPException(
            status_code=404,
            detail="Production batch not found",
        )
    )

    with pytest.raises(HTTPException) as exc:
        service.consume_material(make_data(), performed_by=1)

    assert exc.value.status_code == 404
    assert material.available_quantity == 100


# ==================================================
# FINISHED GOODS PRODUCTION
# ==================================================

def test_record_finished_goods_success(
    service, db, product, batch, movement
):
    service.check_transaction_number = MagicMock()
    service.get_product = MagicMock(return_value=product)
    service.get_batch = MagicMock(return_value=batch)

    inventory = SimpleNamespace(
        product_id=1,
        available_quantity=50,
        rejected_quantity=0,
    )

    db.query.return_value.filter.return_value.first.return_value = inventory

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ):
        result = service.record_finished_goods(
            make_data(quantity=20),
            performed_by=5,
        )

    assert result == movement
    assert inventory.available_quantity == 70
    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(movement)


def test_record_finished_goods_creates_inventory(
    service, db, product, batch, movement
):
    service.check_transaction_number = MagicMock()
    service.get_product = MagicMock(return_value=product)
    service.get_batch = MagicMock(return_value=batch)

    db.query.return_value.filter.return_value.first.return_value = None

    with (
        patch(
            "services.inventory_service.ProductInventory"
        ) as inventory_model,
        patch(
            "services.inventory_service.InventoryMovement",
            return_value=movement,
        ),
    ):
        inventory_model.return_value = SimpleNamespace(
            product_id=1,
            available_quantity=0,
            rejected_quantity=0,
        )

        result = service.record_finished_goods(
            make_data(quantity=15),
            performed_by=5,
        )

    assert result == movement
    inventory_model.assert_called_once_with(
        product_id=1,
        available_quantity=0,
        rejected_quantity=0,
    )
    db.flush.assert_called_once()
    db.commit.assert_called_once()


def test_record_finished_goods_inactive_product(service):
    service.check_transaction_number = MagicMock()
    service.get_product = MagicMock(
        side_effect=HTTPException(
            status_code=400,
            detail="Product is inactive",
        )
    )

    with pytest.raises(HTTPException) as exc:
        service.record_finished_goods(make_data(), performed_by=1)

    assert exc.value.status_code == 400


# ==================================================
# REJECTED GOODS
# ==================================================

def test_record_rejected_goods_success(
    service, product, batch, movement
):
    service.check_transaction_number = MagicMock()
    service.get_product = MagicMock(return_value=product)
    service.get_batch = MagicMock(return_value=batch)

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ):
        result = service.record_rejected_goods(
            make_data(quantity=5),
            performed_by=5,
        )

    assert result == movement
    service.db.add.assert_called_once_with(movement)
    service.db.commit.assert_called_once()
    service.db.refresh.assert_called_once_with(movement)


def test_record_rejected_goods_batch_not_found(service, product):
    service.check_transaction_number = MagicMock()
    service.get_product = MagicMock(return_value=product)
    service.get_batch = MagicMock(
        side_effect=HTTPException(
            status_code=404,
            detail="Production batch not found",
        )
    )

    with pytest.raises(HTTPException) as exc:
        service.record_rejected_goods(make_data(), performed_by=1)

    assert exc.value.status_code == 404
    service.db.add.assert_not_called()


# ==================================================
# STOCK ADJUSTMENT
# ==================================================

def test_adjust_stock_positive_success(service, material, movement):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ):
        result = service.adjust_stock(
            make_data(quantity=25),
            performed_by=5,
        )

    assert result == movement
    assert material.available_quantity == 125
    service.db.add.assert_called_once_with(movement)
    service.db.commit.assert_called_once()


def test_adjust_stock_negative_success(service, material, movement):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)

    with patch(
        "services.inventory_service.InventoryMovement",
        return_value=movement,
    ):
        result = service.adjust_stock(
            make_data(quantity=-30),
            performed_by=5,
        )

    assert result == movement
    assert material.available_quantity == 70


def test_adjust_stock_cannot_be_negative(service, material):
    service.check_transaction_number = MagicMock()
    service.get_material = MagicMock(return_value=material)

    with pytest.raises(HTTPException) as exc:
        service.adjust_stock(
            make_data(quantity=-150),
            performed_by=1,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Stock adjustment cannot make inventory negative"
    )

    assert material.available_quantity == 100
    service.db.add.assert_not_called()
    service.db.commit.assert_not_called()


# ==================================================
# INVENTORY HISTORY
# ==================================================

def test_get_history_success(service, movement):
    service.repository.get_list.return_value = ([movement], 21)

    result = service.get_history(
        movement_type="Raw Material Receipt",
        material_id=1,
        page=2,
        page_size=10,
    )

    assert result["items"] == [movement]
    assert result["total"] == 21
    assert result["page"] == 2
    assert result["page_size"] == 10
    assert result["total_pages"] == 3

    service.repository.get_list.assert_called_once_with(
        movement_type="Raw Material Receipt",
        material_id=1,
        product_id=None,
        production_batch_id=None,
        page=2,
        page_size=10,
    )


def test_get_history_empty(service):
    service.repository.get_list.return_value = ([], 0)

    result = service.get_history()

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


def test_get_history_invalid_page(service):
    with pytest.raises(HTTPException) as exc:
        service.get_history(page=0)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Page must be at least 1"


@pytest.mark.parametrize("page_size", [0, 101])
def test_get_history_invalid_page_size(service, page_size):
    with pytest.raises(HTTPException) as exc:
        service.get_history(page_size=page_size)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Page size must be between 1 and 100"


def test_get_history_invalid_movement_type(service):
    with pytest.raises(HTTPException) as exc:
        service.get_history(movement_type="Invalid Movement")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid movement type"


@pytest.mark.parametrize(
    "movement_type",
    [
        "Raw Material Receipt",
        "Material Consumption",
        "Finished Goods Production",
        "Rejected Goods",
        "Stock Adjustment",
    ],
)
def test_get_history_allowed_movement_types(
    service, movement_type
):
    service.repository.get_list.return_value = ([], 0)

    result = service.get_history(movement_type=movement_type)

    assert result["total"] == 0
    service.repository.get_list.assert_called_once()


# ==================================================
# GET INVENTORY TRANSACTION
# ==================================================

def test_get_transaction_success(service, movement):
    service.repository.get_by_id.return_value = movement

    result = service.get_transaction(1)

    assert result == movement
    service.repository.get_by_id.assert_called_once_with(1)


def test_get_transaction_not_found(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_transaction(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Inventory transaction not found"