import requests
import pytest
import allure
from config import Authorization_key, Phone, company_id

base_url = "https://api.gectaro.com/v1"


@pytest.mark.parametrize(
    "is_authorized, expected_status_code", [(True, 200), (False, 401)]
)
@allure.title("Получение текущего пользователя")
def test_get_current_user(
    validate_project_response, is_authorized, expected_status_code
):
    url = f"{base_url}/users/current"
    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }
    params = {"expand": Phone}

    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        validate_project_response(response_data, "user")


@pytest.mark.parametrize(
    "is_authorized, expected_status_code", [(True, 200), (False, 401)]
)
@allure.title("Получение списка компаний")
def test_get_id_companies(
    validate_project_response, is_authorized, expected_status_code
):
    url = f"{base_url}/companies"

    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        validate_project_response(response_data, "GetAllCompanies")


@pytest.mark.parametrize(
    "company_id_param, expected_status_code, is_authorized",
    [
        (19181, 200, True),
        (19182, 403, True),
        (99999, 400, True),
        (19181, 401, False),
    ],
)
@allure.title("Получение информации о компании по ID")
def test_get_info_companies_id(
    company_id_param, expected_status_code, is_authorized, validate_project_response
):
    url = f"{base_url}/companies/{company_id_param}"
    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == expected_status_code
    response_data = response.json()

    if response.status_code == 200:
        validate_project_response(response_data, "Info company")


@pytest.mark.parametrize(
    "company_id_param, expected_status_code, is_authorized",
    [
        (19181, 200, True),
        (19182, 403, True),
        (99999, 400, True),
        (19181, 401, False),
    ],
)
@allure.title("Получение проектов компании по ID")
def test_get_company_projects(
    company_id_param, expected_status_code, is_authorized, validate_project_response
):
    url = f"{base_url}/companies/{company_id_param}/projects"
    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == expected_status_code
    response_data = response.json()

    if response.status_code == 200:
        validate_project_response(response_data, "Get projects")


@pytest.mark.parametrize(
    "is_authorized, expected_status_code", [(True, 200), (False, 401)]
)
@allure.title("Создание нового проекта")
def test_create_projects(
    validate_project_response, project_id_store, expected_status_code, is_authorized
):
    url = f"{base_url}/companies/{company_id}/projects"

    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    data = {"name": "test"}

    response = requests.post(url, headers=headers, data=data)
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        response_data = response.json()
        validate_project_response(response_data, "Project id")
        project_id_store["project_id"] = response_data["id"]


@pytest.mark.parametrize(
    "is_authorized, expected_status_code", [(True, 200), (False, 401)]
)
@allure.title("Получение информации о проекте по ID")
def test_get_project_id(
    validate_project_response, project_id_store, expected_status_code, is_authorized
):
    project_id = project_id_store.get("project_id")
    assert (
        project_id is not None
    ), "Project ID is not available. Test 'test_create_projects' might have failed."

    url = f"{base_url}/companies/{company_id}/projects/{project_id}"

    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        response_data = response.json()
        validate_project_response(response_data, "Project id")


@pytest.mark.parametrize(
    "update_data, expected_status_code, description, is_authorized",
    [
        (
            {"name": "test_rename", "description": "desc_1", "address": "address_1"},
            200,
            "Valid case: Update name, description, and address",
            True,
        ),
        (
            {"name": None, "description": "desc_1", "address": "address_1"},
            422,
            "Invalid case: 'name' = None",
            True,
        ),
        (
            {"name": "test_rename_2", "description": None, "address": "address_2"},
            200,
            "Valid case 'description' = None",
            True,
        ),
        (
            {"name": "test_rename_3", "description": "desc_3", "address": None},
            200,
            "Valid case: 'address' = None",
            True,
        ),
        (
            {"name": "test_rename", "description": "desc_1", "address": "address_1"},
            401,
            "Unauthorized case",
            False,
        ),
    ],
)
@allure.title("Обновление проекта")
def test_update_project(
    validate_project_response,
    project_id_store,
    update_data,
    expected_status_code,
    description,
    is_authorized,
):
    project_id = project_id_store.get("project_id")
    assert (
        project_id is not None
    ), "Project ID is not available. Test 'test_create_projects' might have failed."

    url = f"{base_url}/companies/{company_id}/projects/{project_id}"

    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.put(url, headers=headers, data=update_data)
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        response_data = response.json()
        validate_project_response(response_data, "Project id")

        for key, value in update_data.items():
            assert (
                response_data[key] == value
            ), f"{key} was not updated correctly: {description}"


@pytest.mark.parametrize(
    "expected_status_code, is_authorized", [(204, True), (401, False), (404, True)]
)
@allure.title("Удаление проекта")
def test_delete_project(
    validate_project_response, project_id_store, expected_status_code, is_authorized
):
    project_id = project_id_store["project_id"]
    assert (
        project_id is not None
    ), "Project ID is not available. Test 'test_create_projects' might have failed."

    url = f"{base_url}/companies/{company_id}/projects/{project_id}"
    headers = {
        "accept": "*/*",
        "Authorization": Authorization_key if is_authorized else None,
    }

    response = requests.delete(url, headers=headers)
    assert response.status_code == expected_status_code


if __name__ == "__main__":
    pytest.main()
