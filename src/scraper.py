from __future__ import annotations

import logging
from typing import Any, AsyncGenerator
from urllib.parse import quote_plus

import httpx

from .models import AdverseEventRecord, PatientDrug, PatientReaction, ScraperInput
from .utils import RateLimiter

logger = logging.getLogger(__name__)


class FDAAdverseEventsScraper:
    """Scraper for FDA Adverse Event Reporting System (FAERS) data via openFDA API."""

    BASE_URL = "https://api.fda.gov/drug/event.json"

    def __init__(self, client: httpx.AsyncClient, rate_limiter: RateLimiter, config: ScraperInput):
        self.client = client
        self.rate_limiter = rate_limiter
        self.config = config

    def build_search_query(self) -> str:
        """Build the search query based on the scraping mode and input parameters."""
        query_parts = []

        if self.config.mode.value == "search_events" and self.config.query:
            # General search across all fields
            query_parts.append(f'"{self.config.query}"')
        
        elif self.config.mode.value == "search_by_drug":
            drug_queries = []
            if self.config.drug_name:
                drug_queries.append(f'patient.drug.medicinalproduct:"{self.config.drug_name}"')
            if self.config.brand_name:
                drug_queries.append(f'patient.drug.medicinalproduct:"{self.config.brand_name}"')
            if self.config.generic_name:
                drug_queries.append(f'patient.drug.medicinalproduct:"{self.config.generic_name}"')
            if drug_queries:
                query_parts.append(f"({' OR '.join(drug_queries)})")

        elif self.config.mode.value == "search_by_reaction":
            if self.config.reaction:
                query_parts.append(f'patient.reaction.reactionmeddrapt:"{self.config.reaction}"')

        elif self.config.mode.value == "search_by_date_range":
            if self.config.date_from and self.config.date_to:
                query_parts.append(f"receivedate:[{self.config.date_from}+TO+{self.config.date_to}]")

        # Add additional filters
        if self.config.serious_only:
            query_parts.append("serious:1")

        if self.config.country:
            query_parts.append(f'occurcountry:"{self.config.country}"')

        if self.config.manufacturer:
            query_parts.append(f'patient.drug.openfda.manufacturer_name:"{self.config.manufacturer}"')

        if self.config.patient_sex:
            sex_code = "1" if self.config.patient_sex.lower() == "male" else "2" if self.config.patient_sex.lower() == "female" else ""
            if sex_code:
                query_parts.append(f"patient.patientsex:{sex_code}")

        # Age range filter
        if self.config.patient_age_min > 0:
            query_parts.append(f"patient.patientonsetage:[{self.config.patient_age_min}+TO+*]")
        if self.config.patient_age_max < 150:
            query_parts.append(f"patient.patientonsetage:[*+TO+{self.config.patient_age_max}]")

        return "+AND+".join(query_parts) if query_parts else ""

    async def fetch_page(self, search_query: str, skip: int = 0, limit: int = 100) -> dict[str, Any]:
        """Fetch a page of results from the openFDA API."""
        params = {
            "limit": min(limit, 1000),  # API max limit is 1000
            "skip": skip,
        }
        
        if search_query:
            params["search"] = search_query

        url = self.BASE_URL
        
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(
                url,
                params=params,
                timeout=self.config.timeout_secs,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("No results found for query: %s", search_query)
                return {"meta": {"results": {"total": 0}}, "results": []}
            raise
        except Exception as e:
            logger.error("Error fetching data: %s", e)
            raise

    def parse_adverse_event(self, raw_event: dict[str, Any]) -> AdverseEventRecord:
        """Parse a raw adverse event record from the API into our structured format."""
        
        # Parse patient reactions
        reactions = []
        if "patient" in raw_event and "reaction" in raw_event["patient"]:
            for reaction_data in raw_event["patient"]["reaction"]:
                reaction = PatientReaction(
                    reaction_term=reaction_data.get("reactionmeddrapt", ""),
                    reaction_outcome=reaction_data.get("reactionoutcome", ""),
                )
                reactions.append(reaction)

        # Parse patient drugs
        drugs = []
        if "patient" in raw_event and "drug" in raw_event["patient"]:
            for drug_data in raw_event["patient"]["drug"]:
                # Get brand/generic names from openfda if available
                brand_name = ""
                generic_name = ""
                manufacturer = ""
                
                if "openfda" in drug_data:
                    brand_names = drug_data["openfda"].get("brand_name", [])
                    generic_names = drug_data["openfda"].get("generic_name", [])
                    manufacturers = drug_data["openfda"].get("manufacturer_name", [])
                    
                    brand_name = brand_names[0] if brand_names else ""
                    generic_name = generic_names[0] if generic_names else ""
                    manufacturer = manufacturers[0] if manufacturers else ""

                drug = PatientDrug(
                    drug_name=drug_data.get("medicinalproduct", ""),
                    brand_name=brand_name,
                    generic_name=generic_name,
                    manufacturer=manufacturer,
                    dose=drug_data.get("drugdosagetext", ""),
                    route=drug_data.get("drugadministrationroute", ""),
                    indication=drug_data.get("drugindication", ""),
                    start_date=drug_data.get("drugstartdate", ""),
                    end_date=drug_data.get("drugenddate", ""),
                    characterization=drug_data.get("drugcharacterization", ""),
                )
                drugs.append(drug)

        # Parse patient demographics
        patient_data = raw_event.get("patient", {})
        patient_age = patient_data.get("patientonsetage", "")
        patient_age_unit = patient_data.get("patientonsetageunit", "")
        patient_sex_code = patient_data.get("patientsex", "")
        patient_sex = ""
        if patient_sex_code == "1":
            patient_sex = "Male"
        elif patient_sex_code == "2":
            patient_sex = "Female"

        patient_weight = patient_data.get("patientweight", "")
        patient_weight_unit = patient_data.get("patientweightunit", "")

        return AdverseEventRecord(
            safety_report_id=raw_event.get("safetyreportid", ""),
            safety_report_version=raw_event.get("safetyreportversion", ""),
            report_type=raw_event.get("reporttype", ""),
            receive_date=raw_event.get("receivedate", ""),
            receipt_date=raw_event.get("receiptdate", ""),
            transmission_date=raw_event.get("transmissiondate", ""),
            primary_source_country=raw_event.get("primarysourcecountry", ""),
            occurrence_country=raw_event.get("occurcountry", ""),
            serious=raw_event.get("serious") == "1",
            seriousness_death=raw_event.get("seriousnessdeathdate") is not None or raw_event.get("seriousnessdeath") == "1",
            seriousness_life_threatening=raw_event.get("seriousnesslifethreatening") == "1",
            seriousness_hospitalization=raw_event.get("seriousnesshospitalization") == "1",
            seriousness_disabling=raw_event.get("seriousnessdisabling") == "1",
            seriousness_congenital_anomali=raw_event.get("seriousnesscongenitalanomali") == "1",
            seriousness_other=raw_event.get("seriousnessother") == "1",
            patient_age=patient_age,
            patient_age_unit=patient_age_unit,
            patient_sex=patient_sex,
            patient_weight=patient_weight,
            patient_weight_unit=patient_weight_unit,
            reactions=reactions,
            drugs=drugs,
            company_number=raw_event.get("companynumb", ""),
            sender_organization=raw_event.get("sender", {}).get("senderorganization", ""),
            reporter_country=raw_event.get("primarysource", {}).get("reportercountry", ""),
            reporter_qualification=raw_event.get("primarysource", {}).get("qualification", ""),
        )

    async def scrape(self) -> AsyncGenerator[dict[str, Any], None]:
        """Main scraping method that yields adverse event records."""
        search_query = self.build_search_query()
        
        logger.info("Starting scrape with query: %s", search_query)
        
        # First request to get total count
        first_page = await self.fetch_page(search_query, skip=0, limit=1)
        total_available = first_page.get("meta", {}).get("results", {}).get("total", 0)
        
        if total_available == 0:
            logger.warning("No results found for search query")
            return

        logger.info("Found %d total results available", total_available)
        
        # Calculate how many to actually fetch
        max_to_fetch = min(self.config.max_results, total_available)
        
        # Fetch in batches
        batch_size = 100  # Good balance between efficiency and memory usage
        skip = 0
        fetched_count = 0
        
        while fetched_count < max_to_fetch:
            remaining = max_to_fetch - fetched_count
            current_batch_size = min(batch_size, remaining)
            
            try:
                page_data = await self.fetch_page(search_query, skip=skip, limit=current_batch_size)
                results = page_data.get("results", [])
                
                if not results:
                    logger.warning("No more results available")
                    break
                
                for raw_event in results:
                    if fetched_count >= max_to_fetch:
                        break
                    
                    try:
                        parsed_event = self.parse_adverse_event(raw_event)
                        yield parsed_event.dict()
                        fetched_count += 1
                    except Exception as e:
                        logger.error("Error parsing event %s: %s", raw_event.get("safetyreportid", "unknown"), e)
                        continue
                
                skip += len(results)
                
                # Break if we got fewer results than requested (end of data)
                if len(results) < current_batch_size:
                    break
                    
            except Exception as e:
                logger.error("Error fetching batch starting at %d: %s", skip, e)
                # Try to continue with next batch
                skip += batch_size
                continue
        
        logger.info("Scraping completed. Fetched %d records", fetched_count)