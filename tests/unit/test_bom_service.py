from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from services.bom_service import BOMService


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
    with patch("services.bom_service.BOMRepository") as repo_class:
        bom_service = BOMService(db)
        bom_service.repository = repo_class.return_value
        yield bom_service


@pytest.fixture
def active_product():
    return SimpleNamespace(
        id=1,
        name="Laptop",
        status="Active",
    )


@pytest.fixture
def inactive_product():
    return SimpleNamespace(
        id=1,
        name="Laptop",
        status="Inactive",
    )


@pytest.fixture
def active_material():
    return SimpleNamespace(
        id=10,
        name="Steel",
        status="Active",
    )


@pytest.fixture
def inactive_material():
    return SimpleNamespace(
        id=10,
        name="Steel",
        status="Inactive",
    )


@pytest.fixture
def inactive_bom():
    return SimpleNamespace(
        id=1,
        product_id=1,
        version="1.0",
        status="Inactive",
        description="Initial BOM",
    )


@pytest.fixture
def active_bom():
    return SimpleNamespace(
        id=2,
        product_id=1,
        version="2.0",
        status="Active",
        description="Active BOM",
    )


@pytest.fixture
def bom_item():
    return SimpleNamespace(
        id=1,
        bom_id=1,
        material_id=10,
        quantity_required=5,
    )


def make_data(**kwargs):
    return SimpleNamespace(**kwargs)


def make_update_data(**kwargs):
    return SimpleNamespace(
        model_dump=lambda exclude_unset=True: kwargs.copy()
    )


# ==================================================
# PRODUCT VALIDATION
# ==================================================

def test_validate_product_success(service, db, active_product):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )

    result = service.validate_product(1)

    assert result == active_product


def test_validate_product_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.validate_product(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"


def test_validate_product_inactive(service, db, inactive_product):
    db.query.return_value.filter.return_value.first.return_value = (
        inactive_product
    )

    with pytest.raises(HTTPException) as exc:
        service.validate_product(1)

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "BOM can only be created for an active product"
    )


# ==================================================
# MATERIAL VALIDATION
# ==================================================

def test_validate_material_success(service, db, active_material):
    db.query.return_value.filter.return_value.first.return_value = (
        active_material
    )

    result = service.validate_material(10)

    assert result == active_material


def test_validate_material_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.validate_material(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Material not found"


def test_validate_material_inactive(service, db, inactive_material):
    db.query.return_value.filter.return_value.first.return_value = (
        inactive_material
    )

    with pytest.raises(HTTPException) as exc:
        service.validate_material(10)

    assert exc.value.status_code == 400
    assert exc.value.detail == (
        "Only active materials can be added to BOM"
    )


# ==================================================
# CREATE BOM
# ==================================================

def test_create_bom_success(
    service, db, active_product, inactive_bom
):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )

    service.repository.get_by_product_version.return_value = None
    service.repository.create_bom.return_value = inactive_bom

    data = make_data(
        product_id=1,
        version="1.0",
        status="Inactive",
        description="Initial BOM",
    )

    result = service.create_bom(data)

    assert result == inactive_bom
    service.repository.create_bom.assert_called_once()


def test_create_bom_invalid_status(service, db, active_product):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )

    data = make_data(
        product_id=1,
        version="1.0",
        status="Invalid",
        description="Test",
    )

    with pytest.raises(HTTPException) as exc:
        service.create_bom(data)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid BOM status"


def test_create_bom_duplicate_version(
    service, db, active_product, inactive_bom
):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )

    service.repository.get_by_product_version.return_value = inactive_bom

    data = make_data(
        product_id=1,
        version="1.0",
        status="Inactive",
        description="Duplicate BOM",
    )

    with pytest.raises(HTTPException) as exc:
        service.create_bom(data)

    assert exc.value.status_code == 409
    assert exc.value.detail == (
        "BOM version already exists for this product"
    )

    service.repository.create_bom.assert_not_called()


def test_create_active_bom_deactivates_existing(
    service, db, active_product, active_bom
):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )

    service.repository.get_by_product_version.return_value = None
    service.repository.get_active_by_product.return_value = active_bom

    data = make_data(
        product_id=1,
        version="3.0",
        status="Active",
        description="New active BOM",
    )

    service.create_bom(data)

    assert active_bom.status == "Inactive"
    service.repository.update_bom.assert_called_once_with(active_bom)
    service.repository.create_bom.assert_called_once()


# ==================================================
# GET BOM
# ==================================================

def test_get_bom_success(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom

    result = service.get_bom(1)

    assert result == inactive_bom


def test_get_bom_not_found(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_bom(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "BOM not found"


# ==================================================
# GET BOM DETAILS
# ==================================================

def test_get_bom_details_success(service, inactive_bom, bom_item):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_items.return_value = [bom_item]

    result = service.get_bom_details(1)

    assert result["id"] == 1
    assert result["product_id"] == 1
    assert result["version"] == "1.0"
    assert result["status"] == "Inactive"
    assert result["description"] == "Initial BOM"
    assert result["items"] == [bom_item]


# ==================================================
# LIST BOM / PAGINATION
# ==================================================

def test_get_boms_success(service, inactive_bom):
    service.repository.get_all.return_value = ([inactive_bom], 21)

    result = service.get_boms(
        product_id=1,
        status="Inactive",
        page=2,
        page_size=10,
    )

    assert result["items"] == [inactive_bom]
    assert result["total"] == 21
    assert result["page"] == 2
    assert result["page_size"] == 10
    assert result["total_pages"] == 3


def test_get_boms_empty_result(service):
    service.repository.get_all.return_value = ([], 0)

    result = service.get_boms()

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


def test_get_boms_invalid_page(service):
    with pytest.raises(HTTPException) as exc:
        service.get_boms(page=0)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Page must be greater than 0"


@pytest.mark.parametrize("page_size", [0, 101])
def test_get_boms_invalid_page_size(service, page_size):
    with pytest.raises(HTTPException) as exc:
        service.get_boms(page_size=page_size)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Page size must be between 1 and 100"


def test_get_boms_invalid_status(service):
    with pytest.raises(HTTPException) as exc:
        service.get_boms(status="Unknown")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid BOM status"


# ==================================================
# UPDATE BOM
# ==================================================

def test_update_bom_success(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.update_bom.return_value = inactive_bom

    data = make_update_data(
        description="Updated BOM description"
    )

    result = service.update_bom(1, data)

    assert result == inactive_bom
    assert inactive_bom.description == "Updated BOM description"
    service.repository.update_bom.assert_called_once_with(inactive_bom)


def test_update_bom_duplicate_version(
    service, inactive_bom, active_bom
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_by_product_version.return_value = active_bom

    data = make_update_data(version="2.0")

    with pytest.raises(HTTPException) as exc:
        service.update_bom(1, data)

    assert exc.value.status_code == 409
    assert exc.value.detail == "BOM version already exists"


def test_update_bom_same_version_allowed(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_by_product_version.return_value = inactive_bom
    service.repository.update_bom.return_value = inactive_bom

    data = make_update_data(version="1.0")

    result = service.update_bom(1, data)

    assert result == inactive_bom
    service.repository.update_bom.assert_called_once_with(inactive_bom)


# ==================================================
# DELETE BOM
# ==================================================

def test_delete_bom_success(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom

    result = service.delete_bom(1)

    assert result == {"message": "BOM deleted successfully"}
    service.repository.delete_bom.assert_called_once_with(inactive_bom)


def test_delete_bom_not_found(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.delete_bom(999)

    assert exc.value.status_code == 404
    service.repository.delete_bom.assert_not_called()


# ==================================================
# ACTIVATE / DEACTIVATE BOM
# ==================================================

def test_update_status_activate_bom(
    service, inactive_bom, active_bom
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_active_by_product.return_value = active_bom
    service.repository.update_bom.side_effect = lambda bom: bom

    result = service.update_status(1, "Active")

    assert active_bom.status == "Inactive"
    assert inactive_bom.status == "Active"
    assert result == inactive_bom
    assert service.repository.update_bom.call_count == 2


def test_update_status_deactivate_bom(service, active_bom):
    service.repository.get_by_id.return_value = active_bom
    service.repository.update_bom.return_value = active_bom

    result = service.update_status(2, "Inactive")

    assert result.status == "Inactive"
    service.repository.update_bom.assert_called_once_with(active_bom)


def test_update_status_invalid(service):
    with pytest.raises(HTTPException) as exc:
        service.update_status(1, "Pending")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid BOM status"

    service.repository.get_by_id.assert_not_called()


# ==================================================
# ADD MATERIAL
# ==================================================

def test_add_material_success(
    service, db, inactive_bom, active_material
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = None

    db.query.return_value.filter.return_value.first.return_value = (
        active_material
    )

    expected_item = SimpleNamespace(
        bom_id=1,
        material_id=10,
        quantity_required=5,
    )
    service.repository.create_item.return_value = expected_item

    data = make_data(
        material_id=10,
        quantity_required=5,
    )

    result = service.add_material(1, data)

    assert result == expected_item
    service.repository.create_item.assert_called_once()


def test_add_material_active_bom_forbidden(service, active_bom):
    service.repository.get_by_id.return_value = active_bom

    data = make_data(
        material_id=10,
        quantity_required=5,
    )

    with pytest.raises(HTTPException) as exc:
        service.add_material(2, data)

    assert exc.value.status_code == 400
    assert "Create a new BOM version" in exc.value.detail
    service.repository.create_item.assert_not_called()


def test_add_material_duplicate(
    service, db, inactive_bom, active_material, bom_item
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = bom_item

    db.query.return_value.filter.return_value.first.return_value = (
        active_material
    )

    data = make_data(
        material_id=10,
        quantity_required=5,
    )

    with pytest.raises(HTTPException) as exc:
        service.add_material(1, data)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Material already exists in this BOM"


# ==================================================
# UPDATE MATERIAL QUANTITY
# ==================================================

def test_update_material_success(
    service, inactive_bom, bom_item
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = bom_item
    service.repository.update_item.return_value = bom_item

    data = make_data(quantity_required=12)

    result = service.update_material(1, 10, data)

    assert result == bom_item
    assert bom_item.quantity_required == 12
    service.repository.update_item.assert_called_once_with(bom_item)


def test_update_material_active_bom_forbidden(service, active_bom):
    service.repository.get_by_id.return_value = active_bom

    with pytest.raises(HTTPException) as exc:
        service.update_material(
            2, 10, make_data(quantity_required=10)
        )

    assert exc.value.status_code == 400


def test_update_material_not_found(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.update_material(
            1, 999, make_data(quantity_required=10)
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Material not found in BOM"


# ==================================================
# REMOVE MATERIAL
# ==================================================

def test_remove_material_success(
    service, inactive_bom, bom_item
):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = bom_item

    result = service.remove_material(1, 10)

    assert result == {
        "message": "Material removed from BOM successfully"
    }
    service.repository.delete_item.assert_called_once_with(bom_item)


def test_remove_material_active_bom_forbidden(service, active_bom):
    service.repository.get_by_id.return_value = active_bom

    with pytest.raises(HTTPException) as exc:
        service.remove_material(2, 10)

    assert exc.value.status_code == 400
    service.repository.delete_item.assert_not_called()


def test_remove_material_not_found(service, inactive_bom):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_item.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.remove_material(1, 999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Material not found in BOM"


# ==================================================
# GET BOM MATERIALS
# ==================================================

def test_get_materials_success(service, inactive_bom, bom_item):
    service.repository.get_by_id.return_value = inactive_bom
    service.repository.get_items.return_value = [bom_item]

    result = service.get_materials(1)

    assert result == [bom_item]
    service.repository.get_items.assert_called_once_with(1)


def test_get_materials_bom_not_found(service):
    service.repository.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_materials(999)

    assert exc.value.status_code == 404


# ==================================================
# PRODUCT BOM HISTORY
# ==================================================

def test_get_product_boms_success(
    service, db, active_product, inactive_bom
):
    db.query.return_value.filter.return_value.first.return_value = (
        active_product
    )
    service.repository.get_product_boms.return_value = [inactive_bom]

    result = service.get_product_boms(1)

    assert result == [inactive_bom]
    service.repository.get_product_boms.assert_called_once_with(1)


def test_get_product_boms_product_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.get_product_boms(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"