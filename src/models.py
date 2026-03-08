from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScrapingMode(str, Enum):
    SEARCH_EVENTS = "search_events"
    SEARCH_BY_DRUG = "search_by_drug"
    SEARCH_BY_REACTION = "search_by_reaction"
    SEARCH_BY_DATE_RANGE = "search_by_date_range"


class ScraperInput(BaseModel):
    mode: ScrapingMode = ScrapingMode.SEARCH_EVENTS
    query: str = ""
    drug_name: str = ""
    reaction: str = ""
    brand_name: str = ""
    generic_name: str = ""
    manufacturer: str = ""
    date_from: str = ""
    date_to: str = ""
    serious_only: bool = False
    country: str = ""
    patient_age_min: int = 0
    patient_age_max: int = 150
    patient_sex: str = ""
    max_results: int = 100
    fields: list[str] = Field(default_factory=list)
    request_interval_secs: float = 0.2
    timeout_secs: int = 30
    max_retries: int = 5

    @classmethod
    def from_actor_input(cls, raw: dict[str, Any]) -> ScraperInput:
        return cls(
            mode=raw.get("mode", ScrapingMode.SEARCH_EVENTS),
            query=raw.get("query", ""),
            drug_name=raw.get("drugName", "") or raw.get("drug_name", ""),
            reaction=raw.get("reaction", ""),
            brand_name=raw.get("brandName", "") or raw.get("brand_name", ""),
            generic_name=raw.get("genericName", "") or raw.get("generic_name", ""),
            manufacturer=raw.get("manufacturer", ""),
            date_from=raw.get("dateFrom", "") or raw.get("date_from", ""),
            date_to=raw.get("dateTo", "") or raw.get("date_to", ""),
            serious_only=raw.get("seriousOnly", False),
            country=raw.get("country", ""),
            patient_age_min=raw.get("patientAgeMin", 0),
            patient_age_max=raw.get("patientAgeMax", 150),
            patient_sex=raw.get("patientSex", "") or raw.get("patient_sex", ""),
            max_results=raw.get("maxResults", 100),
            fields=raw.get("fields", []),
            request_interval_secs=raw.get("requestIntervalSecs", 0.2),
            timeout_secs=raw.get("timeoutSecs", 30),
            max_retries=raw.get("maxRetries", 5),
        )

    def validate_for_mode(self) -> str | None:
        if self.mode == ScrapingMode.SEARCH_BY_DRUG:
            if not (self.drug_name or self.brand_name or self.generic_name):
                return "Provide a drug name, brand name, or generic name for search_by_drug mode."
        if self.mode == ScrapingMode.SEARCH_BY_REACTION:
            if not self.reaction:
                return "Provide a reaction term (e.g., 'headache', 'nausea') for search_by_reaction mode."
        if self.mode == ScrapingMode.SEARCH_BY_DATE_RANGE:
            if not (self.date_from and self.date_to):
                return "Provide both date_from and date_to (YYYYMMDD format) for search_by_date_range mode."
        if self.mode == ScrapingMode.SEARCH_EVENTS:
            if not (self.query or self.drug_name or self.reaction or self.brand_name or self.generic_name):
                return "Provide at least one of: query, drug_name, brand_name, generic_name, or reaction for search_events."
        return None


class PatientReaction(BaseModel):
    reaction_term: str = ""
    reaction_outcome: str = ""


class PatientDrug(BaseModel):
    drug_name: str = ""
    brand_name: str = ""
    generic_name: str = ""
    manufacturer: str = ""
    dose: str = ""
    route: str = ""
    indication: str = ""
    start_date: str = ""
    end_date: str = ""
    characterization: str = ""


class AdverseEventRecord(BaseModel):
    schema_version: str = "1.0"
    type: str = "adverse_event"
    safety_report_id: str = ""
    safety_report_version: str = ""
    report_type: str = ""
    receive_date: str = ""
    receipt_date: str = ""
    transmission_date: str = ""
    primary_source_country: str = ""
    occurrence_country: str = ""
    serious: bool = False
    seriousness_death: bool = False
    seriousness_life_threatening: bool = False
    seriousness_hospitalization: bool = False
    seriousness_disabling: bool = False
    seriousness_congenital_anomali: bool = False
    seriousness_other: bool = False
    patient_age: str = ""
    patient_age_unit: str = ""
    patient_sex: str = ""
    patient_weight: str = ""
    patient_weight_unit: str = ""
    reactions: list[PatientReaction] = Field(default_factory=list)
    drugs: list[PatientDrug] = Field(default_factory=list)
    company_number: str = ""
    sender_organization: str = ""
    reporter_country: str = ""
    reporter_qualification: str = ""