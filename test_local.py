import asyncio
import json
from src.models import ScraperInput, ScrapingMode
from src.scraper import FDAAdverseEventsScraper
from src.utils import RateLimiter
import httpx

async def test_scraper():
    """Simple test to verify the scraper works with the openFDA API."""
    
    # Test configuration
    config = ScraperInput(
        mode=ScrapingMode.SEARCH_BY_REACTION,
        reaction="headache",
        max_results=5,
        request_interval_secs=0.5
    )
    
    print(f"Testing FDA Adverse Events Scraper...")
    print(f"Mode: {config.mode.value}")
    print(f"Reaction: {config.reaction}")
    print(f"Max results: {config.max_results}")
    print()
    
    async with httpx.AsyncClient() as client:
        rate_limiter = RateLimiter(interval=config.request_interval_secs)
        scraper = FDAAdverseEventsScraper(client, rate_limiter, config)
        
        count = 0
        try:
            async for event in scraper.scrape():
                count += 1
                print(f"Retrieved event #{count}:")
                print(f"  Report ID: {event.get('safety_report_id', 'N/A')}")
                print(f"  Receive Date: {event.get('receive_date', 'N/A')}")
                print(f"  Serious: {event.get('serious', 'N/A')}")
                print(f"  Patient Age: {event.get('patient_age', 'N/A')} {event.get('patient_age_unit', '')}")
                print(f"  Patient Sex: {event.get('patient_sex', 'N/A')}")
                
                reactions = event.get('reactions', [])
                if reactions:
                    print(f"  Reactions: {[r.get('reaction_term', '') for r in reactions]}")
                
                drugs = event.get('drugs', [])
                if drugs:
                    drug_names = [d.get('drug_name', '') for d in drugs[:3]]  # Show first 3
                    print(f"  Drugs: {drug_names}")
                
                print()
                
                if count >= config.max_results:
                    break
                    
        except Exception as e:
            print(f"Error during scraping: {e}")
            return False
    
    print(f"Test completed successfully! Retrieved {count} adverse event reports.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_scraper())
    exit(0 if success else 1)