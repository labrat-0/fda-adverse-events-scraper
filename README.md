# FDA Adverse Events Scraper

**Scrape FDA Adverse Event Reporting System (FAERS) for drug safety signals, adverse reactions, and safety reports.**

Access pharmaceutical safety data that biotech companies pay $30K+/year for - completely free. No API keys required.

[![Apify](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/labrat011/fda-adverse-events-scraper)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## What This Scraper Does

This actor extracts adverse event reports from the **FDA Adverse Event Reporting System (FAERS)** via the free openFDA API. FAERS contains millions of reports about:

- Drug side effects and adverse reactions
- Medication errors  
- Product quality problems
- Serious safety events (deaths, hospitalizations, disabilities)
- Patient demographics and outcomes

Perfect for **pharmaceutical companies**, **biotech firms**, **researchers**, and **healthcare organizations** conducting drug safety analysis and competitive intelligence.

## 🚀 Key Features

- **No API Key Required** - Uses free openFDA public API
- **Multiple Search Modes** - Drug names, reactions, date ranges, general queries
- **Rich Data Output** - Structured adverse event reports with patient demographics
- **Rate Limiting** - Respects API limits with configurable request intervals
- **Batch Processing** - Efficiently handles large datasets
- **Free Tier Available** - 25 results per run for free users

## 👥 Who Uses This

### 🔬 Pharmacovigilance and Drug Safety Teams

You're running signal detection — monitoring adverse event frequencies, tracking serious events (death, hospitalization, disability), and identifying emerging safety patterns before they become regulatory problems. FAERS has millions of reports. This actor gives you structured, filterable access to all of it.

```json
{
    "mode": "search_by_drug",
    "drugName": "OZEMPIC",
    "seriousOnly": true,
    "maxResults": 500
}
```

Filter by `seriousOnly` to focus on death/hospitalization/disability events. Use `search_by_reaction` mode to find all drugs associated with a specific adverse reaction — useful for class-effect signal detection.

---

### 💼 Pharma Competitive Intelligence Teams

You want to understand the real-world safety profile of a competitor's drug — not just what's on the label, but what's being reported post-market. FAERS data often surfaces signals years before label updates. This is the same data pharma companies pay $30K+/year to access through commercial databases.

```json
{
    "mode": "search_by_drug",
    "drugName": "WEGOVY",
    "country": "US",
    "maxResults": 1000
}
```

Compare adverse event frequencies across competing drugs in the same class. Combine with FDA Drug Labels to cross-reference whether reported reactions are already captured in the label or represent unlabeled findings.

---

### 🏢 Biotech and Clinical-Stage Companies

You're doing due diligence on a licensing target, assessing portfolio compound risk, or preparing regulatory submissions. FAERS provides real-world safety evidence to supplement clinical trial data — and it's free, public, and updated quarterly.

```json
{
    "mode": "search_by_date_range",
    "dateFrom": "2023-01-01",
    "dateTo": "2024-01-01",
    "drugName": "KEYTRUDA",
    "maxResults": 500
}
```

Date-range queries let you track how the safety profile of a compound evolves over time — useful for longitudinal analyses in regulatory submissions or pre-licensing technical assessments.

---

### 📰 Healthcare Policy Researchers and Journalists

You're investigating drug safety patterns at the population level — which drugs generate the most serious adverse event reports, which manufacturers have the highest report volumes, which reactions are disproportionately associated with specific compounds.

```json
{
    "mode": "search_by_reaction",
    "reactionName": "suicidal ideation",
    "seriousOnly": true,
    "maxResults": 1000
}
```

Use `search_by_reaction` to find all drugs associated with a specific reaction type. The report source, patient demographics, and outcome fields provide context for investigative analysis without requiring access to commercial pharmacovigilance databases.

---

### 🤖 AI/LLM Engineers and Medical AI Builders

You're building medical AI pipelines that need access to real-world safety data — not just label text, but post-market reports. FAERS data as a RAG source or MCP tool grounds your agent in actual pharmacovigilance evidence.

**MCP tool config:**

```json
{
    "mcpServers": {
        "fda-adverse-events": {
            "url": "https://mcp.apify.com?tools=labrat011/fda-adverse-events-scraper",
            "headers": {
                "Authorization": "Bearer <APIFY_TOKEN>"
            }
        }
    }
}
```

Combine with FDA Drug Labels and Clinical Trials Scraper for a complete drug safety intelligence stack accessible to your AI agent.

---

## 🎯 Input Configuration

### Scraping Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **search_events** | General keyword search | Broad safety surveillance |
| **search_by_drug** | Drug name/brand focused | Product-specific monitoring |
| **search_by_reaction** | Adverse reaction focused | Safety signal detection |
| **search_by_date_range** | Temporal analysis | Trend identification |

### Key Parameters

```json
{
  "mode": "search_by_drug",
  "drugName": "LIPITOR",
  "seriousOnly": true,
  "maxResults": 100,
  "country": "US"
}
```

### Advanced Filtering

- **Drug Filters**: Brand name, generic name, manufacturer
- **Patient Demographics**: Age range, gender  
- **Event Severity**: Serious events only (death, hospitalization, etc.)
- **Geographic**: Filter by country
- **Temporal**: Date range analysis

## 📋 Output Format

Each adverse event report includes:

### Report Metadata
- Safety report ID and version
- Receive/transmission dates  
- Report type and source country
- Sender organization info

### Patient Information
- Demographics (age, sex, weight)
- All reported adverse reactions
- Reaction outcomes and severity

### Drug Details  
- Medicinal product names
- Brand/generic names
- Manufacturer information
- Dosage and administration route
- Treatment indications
- Start/end dates

### Safety Classification
- Serious event indicators
- Death/hospitalization flags
- Life-threatening status
- Disability outcomes

## 💡 Example Queries

### Monitor Statin Safety Events
```json
{
  "mode": "search_by_drug", 
  "drugName": "atorvastatin",
  "seriousOnly": true,
  "maxResults": 200
}
```

### Track COVID Vaccine Reactions  
```json
{
  "mode": "search_events",
  "query": "COVID vaccine",
  "dateFrom": "20210101",
  "dateTo": "20231231"
}
```

### Analyze Heart Attack Reports
```json
{
  "mode": "search_by_reaction",
  "reaction": "myocardial infarction", 
  "patientAgeMin": 40,
  "patientAgeMax": 80
}
```

### Pharmaceutical Company Analysis
```json
{
  "mode": "search_events",
  "manufacturer": "Pfizer",
  "seriousOnly": true,
  "country": "US"
}
```

## 📈 Sample Output

```json
{
  "schema_version": "1.0",
  "type": "adverse_event", 
  "safety_report_id": "10003300",
  "receive_date": "20140306",
  "serious": true,
  "seriousness_hospitalization": true,
  "patient_age": "77",
  "patient_sex": "Female",
  "reactions": [
    {
      "reaction_term": "Myocardial infarction",
      "reaction_outcome": "recovered"
    }
  ],
  "drugs": [
    {
      "drug_name": "LIPITOR",
      "brand_name": "LIPITOR", 
      "generic_name": "atorvastatin",
      "manufacturer": "Pfizer",
      "dose": "20 MG",
      "indication": "HYPERCHOLESTEROLEMIA"
    }
  ]
}
```

## 🔧 Technical Details

### Data Source
- **FDA FAERS Database** via openFDA API
- **Update Frequency**: Quarterly FDA releases  
- **Coverage**: 2004 to present
- **Volume**: Millions of adverse event reports

### Rate Limiting
- Default: 0.2 seconds between requests
- Configurable: 0.1 to 5 seconds
- Automatic retry with exponential backoff
- Respects openFDA API limits

### Data Quality Notes
⚠️ **Important Disclaimers**:
- Reports do not prove causality between drugs and events
- Voluntary reporting system - not all events captured
- Requires medical expertise for interpretation
- FDA does not validate all reports

## 💰 Pricing & Limits

| Plan | Results per Run | Best For |
|------|-----------------|----------|
| **Free** | 25 | Testing, small analyses |
| **Paid** | Up to 1,000 | Enterprise monitoring |

## 🚀 Quick Start

1. **Run on Apify Console**
   - Visit [FDA Adverse Events Scraper](https://apify.com/labrat011/fda-adverse-events-scraper)
   - Configure your search parameters
   - Click "Start" to begin scraping

2. **Integrate via API**
   ```bash
   curl -X POST https://api.apify.com/v2/acts/labrat011~fda-adverse-events-scraper/runs \
     -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "mode": "search_by_drug",
       "drugName": "aspirin",
       "maxResults": 50
     }'
   ```

3. **Use Apify SDK**
   ```python
   from apify_client import ApifyClient
   
   client = ApifyClient("YOUR_API_TOKEN")
   
   run_input = {
       "mode": "search_by_drug", 
       "drugName": "metformin",
       "seriousOnly": True,
       "maxResults": 100
   }
   
   run = client.actor("labrat011/fda-adverse-events-scraper").call(run_input=run_input)
   ```

## 📊 Market Context

### What Companies Pay For This Data
- **Biomedtracker**: $30K-100K/year for safety intelligence
- **Evaluate Pharma**: $50K-200K/year for drug pipeline data
- **Definitive Healthcare**: $50K+/year for adverse event monitoring
- **IQVIA Safety Intelligence**: Custom enterprise pricing

### Why This Matters (2026)
- **$300B Patent Cliff** - Major drugs losing exclusivity
- **AI Drug Discovery Boom** - Need for comprehensive safety data
- **Regulatory Scrutiny** - FDA requiring more post-market surveillance
- **Gene Therapy Expansion** - Novel safety profiles need monitoring

## 🔗 Related Actors

Part of our **Healthcare Data Intelligence Suite**:

- [Clinical Trials Scraper](https://apify.com/labrat011/clinical-trials-scraper) - ClinicalTrials.gov data
- [FDA Drug Labels Scraper](https://apify.com/labrat011/fda-drug-labels-scraper) - Drug labeling info
- [FDA Orange Book Scraper](https://apify.com/labrat011/fda-orange-book-scraper) - Patent/exclusivity data  
- [PubMed Scraper](https://apify.com/labrat011/pubmed-scraper) - Scientific literature

## 🔗 Related Actors

| Actor | What it does | Pairs well when... |
|-------|-------------|---------------------|
| [FDA Drug Labels Scraper](https://apify.com/labrat011/fda-drug-labels-scraper) | FDA-approved drug labeling data | Cross-reference reported adverse reactions with the drug's official label warnings |
| [FDA Orange Book Scraper](https://apify.com/labrat011/fda-orange-book-scraper) | Patent, exclusivity, and generic data | Check market status of drugs generating high adverse event volumes |
| [Clinical Trials Scraper](https://apify.com/labrat011/clinical-trials-scraper) | ClinicalTrials.gov study data | Find active safety monitoring trials for drugs with FAERS signals |
| [PubMed Scraper](https://apify.com/labrat011/pubmed-scraper) | 35M+ biomedical abstracts from NCBI | Find published literature on safety signals identified in FAERS data |
| [NPI Provider Contact Finder](https://apify.com/labrat011/npi-provider-contact-finder) | Healthcare provider directory | Identify prescribers in areas with high adverse event report concentrations |

---

## ⚖️ Legal & Compliance

- Uses **public FDA data** via official openFDA API
- **No personal health information** - all data de-identified
- Complies with FDA transparency initiatives
- Suitable for regulatory submissions and research
- **Apache 2.0 License** - free for commercial use

## 🐛 Issues & Support

- **Report bugs**: [GitHub Issues](https://github.com/labrat-0/fda-adverse-events-scraper/issues)
- **Feature requests**: Open a GitHub issue
- **Documentation**: This README + Apify Console help

## 🏗️ Development

Built with modern Python stack:
- **Python 3.12** - Latest stable Python
- **httpx** - Async HTTP client  
- **Pydantic** - Data validation
- **Apify SDK** - Platform integration

---

**Ready to monitor drug safety at scale? Start scraping FDA adverse events today!**

[🚀 **Try it now on Apify**](https://apify.com/labrat011/fda-adverse-events-scraper)