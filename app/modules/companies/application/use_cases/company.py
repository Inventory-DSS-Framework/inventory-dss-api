"""Companies module — use cases for the Company aggregate.

One class per business action. Repositories (domain ports) are injected by
constructor so the use cases are unit-testable with in-memory fakes.
"""
from __future__ import annotations

from uuid import UUID

from app.modules.companies.application.dtos import CompanyDTO
from app.modules.companies.domain.entities import Company
from app.modules.companies.domain.exceptions import (
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
)
from app.modules.companies.domain.repositories import CompanyRepository
from app.shared.domain.value_objects import Email


class CreateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self._companies = companies

    def execute(
        self,
        *,
        name: str,
        tax_id: str,
        email: str,
        business_type: str = "",
        address: str = "",
        phone: str = "",
    ) -> CompanyDTO:
        if self._companies.get_by_tax_id(tax_id) is not None:
            raise CompanyAlreadyExistsError(tax_id)
        company = Company(
            name=name,
            tax_id=tax_id,
            business_type=business_type,
            address=address,
            phone=phone,
            email=Email(email),
        )
        return CompanyDTO.from_entity(self._companies.add(company))


class GetCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self._companies = companies

    def execute(self, company_id: UUID) -> CompanyDTO:
        company = self._companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError(company_id)
        return CompanyDTO.from_entity(company)


class UpdateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self._companies = companies

    def execute(
        self,
        company_id: UUID,
        *,
        name: str | None = None,
        business_type: str | None = None,
        address: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> CompanyDTO:
        company = self._companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError(company_id)
        if name is not None:
            company.name = name
        if business_type is not None:
            company.business_type = business_type
        if address is not None:
            company.address = address
        if phone is not None:
            company.phone = phone
        if email is not None:
            company.email = Email(email)
        return CompanyDTO.from_entity(self._companies.update(company))


class SuspendCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self._companies = companies

    def execute(self, company_id: UUID) -> CompanyDTO:
        company = self._companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError(company_id)
        company.suspend()
        return CompanyDTO.from_entity(self._companies.update(company))


class ListCompanies:
    def __init__(self, companies: CompanyRepository) -> None:
        self._companies = companies

    def execute(self, offset: int = 0, limit: int = 50) -> list[CompanyDTO]:
        return [CompanyDTO.from_entity(c) for c in self._companies.list(offset, limit)]
