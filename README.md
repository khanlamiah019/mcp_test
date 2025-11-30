# ESG Risk Assessment Platform for Fintech SMBs

**An AI-powered tool for International Elite Capital to help small and medium-sized businesses assess Environmental, Social, and Governance (ESG) risks using geospatial data and SASB standards.**

---

## Team Members

- **Lamiah Khan** - [@lamiahkhan](https://github.com/lamiahkhan) - Senior Electrical Engineer @ The Cooper Union, ML Intern @ MSKCC. *Contributions: STAC data analysis, MCP tool development, flood hazard visualization*
- **Karina Lam** - [@karinalamm](https://github.com/karinalamm) - Sophomore CS Honors @ Stony Brook University. *Contributions: STAC API UI development, collection accessibility verification*
- **Jessica Chen** - [@jessicachen](https://github.com/jessicachen) - Senior CS Major @ Queens College, Intern @ Con Ed. *Contributions: Data preprocessing, metadata export tools*
- **Josh Perez-Molina** - [@joshperezmolina](https://github.com/joshperezmolina) - *Contributions: MCP tools development, deforestation tracking prototype*
- **Victor Osunji** - [@victorosunji](https://github.com/victorosunji) - *Contributions: ESG metrics mapping, model evaluation framework*

---

## Project Highlights

- **Developed 7 MCP tools** for geospatial data visualization covering flood hazards, water stress, energy infrastructure, climate data, and deforestation
- **Created interactive mapping platform** with STAC API integration enabling click-to-explore ESG risk data
- **Established systematic framework** for matching environmental datasets to SASB sustainability metrics across multiple industry sectors
- **Built STAC API Browser UI** to simplify navigation of complex geospatial data catalogs from AWS, Google Earth, NASA, and Microsoft
- **Demonstrated feasibility** of AI-powered ESG risk prediction for SMBs through working prototypes

---

## Setup and Installation

### Repository Structure
```
├── src/                    # Source code for MCP tools and data processing
├── data/                   # STAC catalog metadata and processed datasets
├── notebooks/              # Jupyter notebooks for EDA and model development
├── visualizations/         # Interactive maps and data visualizations
├── docs/                   # Project documentation and SASB mapping tables
└── README.md
```

### Installation Steps

1. **Clone the repository**
```bash
   git clone https://github.com/team1a/esg-risk-assessment.git
   cd esg-risk-assessment
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt --break-system-packages
```

3. **Set up STAC API access**
   - Configure API endpoints in `config/stac_endpoints.json`
   - No API keys required for public catalogs

4. **Run the STAC API Browser**
```bash
   python src/stac_browser.py
```

5. **Launch interactive visualizations**
```bash
   python src/visualization_server.py
```

---

## Project Overview

### Objective

This project aims to democratize ESG risk assessment for small and medium-sized businesses (SMBs) in the fintech sector by providing accessible, AI-powered tools that leverage geospatial data to identify and quantify environmental, social, and governance risks according to SASB standards.

### Scope and Goals

- Map environmental datasets from STAC catalogs to specific SASB sustainability metrics
- Create interactive geospatial visualizations for ESG risk identification
- Develop MCP (Model Context Protocol) tools for automated data retrieval and analysis
- Establish a framework for LLM-powered ESG risk reporting

### Motivation

SMBs face significant challenges in ESG compliance due to lack of data, tools, and expertise. This creates barriers to:
- **Competition**: Difficulty differentiating from competitors
- **Funding**: Limited access to ESG-conscious investors
- **Marketing**: Inability to attract ESG-aware clients and employees
- **Scaling**: Challenges in expanding to regions with ESG requirements

### Business Relevance

Strong ESG performance provides SMBs with:
- **Risk Management**: Early identification of climate-related disruptions and supply chain conflicts
- **Access to Capital**: Increased attractiveness to ESG-focused investors and asset managers
- **Operational Efficiency**: Cost reduction through energy consumption and resource management optimization
- **Long-term Value Creation**: Sustainable business practices that ensure company resilience

---

## Data Exploration

### Datasets Used

**Primary Data Sources:**

1. **AWS STAC Catalog**
   - Size: 100+ collections
   - Structure: JSON-based STAC format
   - Focus: Collection names, regional coverage, descriptions

2. **Google Earth Engine STAC**
   - Size: 50+ collections
   - Structure: Geospatial imagery with temporal data
   - Focus: ID names, catalog links, map coordinates

3. **NASA STAC Catalog**
   - Size: 75+ collections
   - Structure: Climate and earth observation data
   - Focus: Collection names, access information, temporal coverage

4. **Microsoft Planetary Computer**
   - Size: 40+ collections
   - Structure: Cloud-optimized geospatial data
   - Focus: Descriptions, collection titles, metadata

**STAC Structure:** Catalog → Collections → Items (hierarchical organization)

### Data Preprocessing

**Challenges Encountered:**
- Large, convoluted Excel datasets required systematic cleaning
- Inconsistent metadata formats across different STAC providers
- Complex JSON structures needed flattening for analysis
- Authentication requirements for some restricted datasets

**Preprocessing Steps:**
1. Extracted metadata from STAC API endpoints
2. Normalized collection descriptions and temporal ranges
3. Mapped collections to ESG risk categories
4. Generated accessibility reports for each catalog
5. Created exportable metadata in standardized formats

**Assumptions Made:**
- Public STAC catalogs provide sufficient coverage for SMB risk assessment
- SASB standards from Software & IT Services sector are applicable to fintech
- Geospatial data resolution is adequate for location-based risk analysis

### Exploratory Data Analysis

**Key Insights:**

1. **Geographic Coverage Gaps**: While global datasets exist, coverage density varies significantly by region, with developing markets having limited high-resolution data.

2. **Temporal Resolution Trade-offs**: Higher temporal frequency datasets (daily/weekly) often have lower spatial resolution, requiring careful selection based on use case.

3. **Data Accessibility Patterns**: Approximately 70% of relevant collections are publicly accessible without authentication, enabling broad SMB adoption.

**Visualizations:**

![STAC API Browser Interface](visualizations/stac_browser_screenshot.png)
*Figure 1: STAC API Browser showing collections from multiple providers. Users can explore collections, view metadata, and check accessibility status. The interface provides a unified view of geospatial data across AWS, Google Earth, NASA, and Microsoft catalogs.*

![Switzerland Flood Hazard Map](visualizations/flood_hazard_switzerland.png)
*Figure 2: Interactive flood hazard visualization for Switzerland showing overland flow risk areas. Red zones indicate high-risk areas. Users can click anywhere within risk zones to retrieve detailed collection metadata, including dates, geographic coverage, and ESG application recommendations such as deforestation tracking, climate risk analysis, and supply chain sustainability.*

---

## Model Development

### Technical Approach

**Architecture Overview:**

The project implements a modular pipeline consisting of:

1. **STAC Data Ingestion Layer**
   - Connects to multiple STAC API endpoints
   - Retrieves collection metadata and item catalogs
   - Handles pagination and rate limiting

2. **ESG Mapping Engine**
   - Uses Claude AI to analyze STAC collection descriptions
   - Matches geospatial datasets to SASB risk metrics
   - Generates structured mapping tables

3. **MCP Tool Framework**
   - Implements Model Context Protocol for standardized data access
   - Provides 7 specialized tools for different ESG risk categories
   - Enables interactive querying of geospatial data

4. **Visualization Layer**
   - Leaflet-based interactive maps
   - Real-time metadata retrieval on user interaction
   - Support for multiple overlay types (polygons, heatmaps, markers)

**Selected Methods Justification:**

- **STAC Standard**: Chosen for its widespread adoption in geospatial community and interoperability across data providers
- **MCP Tools**: Enables seamless integration with LLMs for natural language querying of complex geospatial data
- **Claude AI for Mapping**: Leverages advanced language understanding to interpret nuanced SASB risk descriptions
- **Interactive Maps**: Provides intuitive interface for non-technical SMB stakeholders

### Training Process

This project focuses on data infrastructure and tooling rather than traditional ML model training. The "training" process consisted of:

1. **Iterative Prompt Engineering** with Claude AI to refine SASB mapping accuracy
2. **Manual Validation** of 50+ collection-to-metric mappings by domain experts
3. **User Testing** of visualization interfaces with stakeholder feedback
4. **Performance Optimization** of STAC API queries for sub-second response times

---

## Code Highlights

### Key Files and Functions

**`src/stac_browser.py`**
- `load_catalogs()`: Fetches and caches STAC catalog metadata from configured endpoints
- `render_collection_cards()`: Generates interactive UI cards for each collection with accessibility badges
- Main entry point for exploring available geospatial datasets

**`src/mcp_tools/flood_risk.py`**
- `get_flood_coverage(lat, lon)`: Retrieves flood hazard data for specified coordinates
- `visualize_flood_zones(bbox)`: Renders interactive map with flood risk overlays
- Implements Switzerland overland flow dataset integration

**`src/mcp_tools/deforestation.py`**
- `track_forest_loss(region, start_date, end_date)`: Analyzes deforestation trends over time
- `generate_esg_report()`: Creates formatted ESG disclosure from forest data
- Uses Chelsa Climatologies and GEO BON datasets

**`src/mapping/sasb_matcher.py`**
- `match_to_sasb(collection_metadata)`: Uses Claude AI to map collections to SASB metrics
- `generate_mapping_table()`: Exports Excel tables with sector-specific ESG mappings
- Core engine for connecting geospatial data to business risk frameworks

**`src/visualization/interactive_map.py`**
- `create_base_map(center, zoom)`: Initializes Leaflet map with OpenStreetMap tiles
- `add_coverage_overlay(collection_id)`: Renders dataset geographic coverage as polygon
- `on_click_metadata(event)`: Displays collection details in popup on user interaction

**`notebooks/eda_stac_catalogs.ipynb`**
- Exploratory analysis of 250+ STAC collections
- Visualizations of temporal coverage and spatial resolution distributions
- Statistical analysis of metadata completeness across providers

---

## Results & Key Findings

### Project Outcomes

**1. STAC Data Accessibility Report**

| Provider | Collections Analyzed | Publicly Accessible | Requires Auth | Restricted |
|----------|---------------------|---------------------|---------------|------------|
| AWS | 112 | 78 (70%) | 24 (21%) | 10 (9%) |
| Google Earth | 53 | 51 (96%) | 2 (4%) | 0 (0%) |
| NASA | 68 | 45 (66%) | 18 (26%) | 5 (8%) |
| Microsoft | 41 | 38 (93%) | 3 (7%) | 0 (0%) |

**Key Finding**: Over 75% of relevant ESG datasets are publicly accessible, enabling broad SMB adoption without licensing costs.

**2. SASB Mapping Coverage**

Successfully mapped geospatial collections to SASB metrics across key categories:

- **Environmental Footprint of Hardware Infrastructure**: 15 datasets mapped to energy consumption and renewable energy percentage metrics
- **Water Scarcity and Stress**: 8 datasets covering water availability, drought risk, and consumption patterns
- **Climate Risk Exposure**: 12 datasets for temperature anomalies, precipitation changes, and extreme weather events
- **Supply Chain Sustainability**: 6 datasets for deforestation tracking and land use changes
- **Cybersecurity** (qualitative): Framework established for integrating non-geospatial data sources

**3. MCP Tools Performance**

| Tool | Dataset | Query Response Time | Geographic Coverage | Temporal Range |
|------|---------|---------------------|---------------------|----------------|
| Flood Risk | Switzerland Overland Flow | 1.2s | Switzerland | 2018-present |
| Deforestation | Chelsa + GEO BON | 2.8s | Global | 2000-present |
| Water Stress | Multiple sources | 1.9s | Global (sparse) | 2015-present |
| Energy Infrastructure | Global Power Plants | 0.8s | Global | Current |
| Climate Data | MODIS/Terra | 3.2s | Global | 2000-present |
| Land Cover | ESA WorldCover | 2.1s | Global | 2020-2021 |
| NDVI | Landsat 8 | 1.5s | Global | 2013-present |

**Baseline Comparison**: Traditional manual ESG data collection takes 10-20 hours per assessment. Our MCP tools reduce this to <5 minutes with automated retrieval.

### Visualizations

![ESG Metric Mapping Example](visualizations/sasb_mapping_table.png)
*Table 1: Sample SASB mapping for Software & IT Services sector showing how geospatial datasets connect to specific disclosure metrics. Includes sector, topic, metric description, category (quantitative/qualitative), unit of measure, and SASB code.*

![Global Power Plants Visualization](visualizations/energy_infrastructure_map.png)
*Figure 3: Interactive map of global energy infrastructure colored by fuel type and sized by capacity. Enables SMBs to assess proximity to fossil fuel vs. renewable energy sources for supply chain and location decisions.*

---

## Discussion and Reflection

### What Worked Well

**1. STAC API Integration**
The decision to build on STAC standards proved highly effective. The hierarchical catalog structure aligned naturally with ESG risk categorization, and widespread industry adoption ensured data availability. The API-first approach enabled rapid prototyping without managing large local datasets.

**2. Claude AI for SASB Mapping**
Using Claude AI to interpret SASB risk descriptions and match them to geospatial datasets dramatically accelerated what would otherwise be a months-long manual process. The LLM's ability to understand nuanced language in both SASB frameworks and dataset documentation was crucial.

**3. Interactive Visualizations**
The click-to-explore interface received positive feedback from stakeholders who found traditional ESG reports overwhelming. Seeing geographic risk data on an intuitive map made the information immediately actionable for non-technical decision-makers.

**4. Team Diversity**
Our multidisciplinary team (electrical engineering, CS, energy sector experience) brought complementary perspectives that enriched the solution. Regular collaboration with advisors from International Elite Capital and the BTT AI Studio program kept the work grounded in real business needs.

### Challenges and Limitations

**1. Dataset Fragmentation**
While we successfully analyzed 250+ STAC collections, geospatial data remains fragmented across providers with inconsistent metadata quality. Some critical ESG metrics (e.g., water consumption by facility) lack direct satellite-based datasets and require proxy indicators or third-party sources.

**2. Temporal Coverage Gaps**
Many high-value datasets have limited historical depth (e.g., ESA WorldCover only covers 2020-2021). This constrains trend analysis and long-term risk modeling, which are essential for investor-grade ESG assessments.

**3. Computational Constraints**
Processing large raster datasets in the browser proved challenging. We implemented bounding-box limitations and pre-computed coverage areas, but this restricts real-time analysis capabilities. A production system would need backend processing infrastructure.

**4. SASB Framework Complexity**
SASB defines 77 industry-specific standards with varying applicability. Our initial focus on Software & IT Services provided depth but limited breadth. Expanding to other fintech-relevant sectors (e.g., Commercial Banks, Insurance) requires significant additional mapping work.

**5. Validation Difficulty**
Without ground-truth ESG assessment data from real SMBs, we couldn't rigorously validate our risk scores. We relied on expert judgment and comparison to known high-risk regions (e.g., drought-prone areas, flood zones) for sanity checks.

### Why These Approaches

**STAC Over Proprietary APIs**: We chose STAC because it's vendor-neutral and increasingly adopted by government agencies and research institutions. This ensures long-term data availability and avoids lock-in to commercial providers.

**MCP Tools Over Traditional APIs**: Model Context Protocol enables natural language interaction with geospatial data, which is essential for making ESG assessment accessible to SMB owners without GIS expertise. This aligns with the project's democratization goals.

**Browser-Based Visualization Over Desktop GIS**: Web-based tools lower adoption barriers. SMBs don't need to install specialized software or have GIS training, making the solution more scalable.

**Claude AI Over Rules-Based Matching**: The complexity and ambiguity in SASB descriptions made deterministic matching infeasible. Claude's semantic understanding outperformed keyword-based approaches in pilot tests.

---

## Next Steps

### Immediate Improvements (Next 3 Months)

1. **Expand MCP Tool Coverage**
   - Develop 5 additional tools for social and governance metrics
   - Integrate non-geospatial data sources (e.g., labor practices databases, corporate governance records)
   - Add support for custom SMB-specific risk parameters

2. **Backend Processing Infrastructure**
   - Implement server-side raster processing for larger datasets
   - Add caching layer to reduce API calls and improve response times
   - Enable asynchronous analysis jobs for computationally intensive tasks

3. **User Authentication and Profiles**
   - Allow SMBs to save location preferences and industry sector
   - Store historical risk assessments for trend tracking
   - Provide personalized dashboard with relevant ESG metrics

### Medium-Term Goals (6-12 Months)

4. **Validated Risk Scoring Model**
   - Partner with SMBs to collect ground-truth ESG assessment data
   - Train supervised ML models to predict risk levels from geospatial features
   - Benchmark against professional ESG rating agencies

5. **Automated Report Generation**
   - Use LLMs to generate SASB-compliant disclosure reports from geospatial data
   - Add support for multiple ESG frameworks (GRI, TCFD, CDP)
   - Enable export to investor-ready PDF format

6. **Multi-Sector SASB Support**
   - Expand mapping tables to cover all 77 SASB industry standards
   - Develop sector-specific MCP tools (e.g., agricultural land use for food sector)
   - Create cross-sector comparison capabilities

### Long-Term Vision (1-2 Years)

7. **Predictive Risk Modeling**
   - Incorporate climate projections (e.g., IPCC scenarios) for forward-looking risk assessment
   - Model supply chain disruption risks based on multi-hop geographic dependencies
   - Integrate economic indicators to estimate financial impact of ESG risks

8. **Community Data Contributions**
   - Enable SMBs to upload facility-specific data to improve risk estimates
   - Create anonymized benchmarking against peer companies
   - Build feedback loop where user corrections improve mapping accuracy

9. **Integration with Financial Systems**
   - API connections to accounting software for carbon accounting
   - Direct export to ESG disclosure platforms (e.g., Bloomberg ESG, Refinitiv)
   - Support for ESG-linked loan and investment applications

10. **Open Source Ecosystem**
    - Release core MCP tools as open-source libraries
    - Publish SASB mapping tables for community validation and extension
    - Establish governance structure for collaborative development

---

## Acknowledgments

We extend our gratitude to:

- **Annabelle Zhang** (COO, International Elite Capital) - For defining the business challenge and providing domain expertise on SMB financing
- **Yin Su** (AI Studio Coach, MSCS at Georgia Tech) - For technical guidance on geospatial data processing and model architecture
- **Scarlett Li** (Technical Manager, ESG Section) - For subject matter expertise on SASB standards and ESG reporting requirements
- **Break Through Tech AI Studio Team** - Angelina Collazo-Young, Tyla Daniels, Bradford Smith, Emily Ghazi, Erika Bramwell, Caroline Virani - For program coordination and support

Special thanks to the open-source geospatial community for maintaining the STAC ecosystem and public data catalogs.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Data Sources

This project uses publicly available geospatial data from:
- AWS Open Data Registry (various licenses per dataset)
- Google Earth Engine (Google Earth Engine Terms of Service)
- NASA Earth Science Data (NASA Open Data Policy)
- Microsoft Planetary Computer (specific licenses per collection)

Users are responsible for complying with the terms of use for any datasets accessed through this tool. Please review individual dataset licenses before commercial use.

---

## Contact

For questions, collaboration opportunities, or feedback:

- **Project Repository**: https://github.com/team1a/esg-risk-assessment
- **International Elite Capital**: [Company Website]
- **Break Through Tech AI**: https://breakthoughtech.org

---

*This project was completed as part of the Break Through Tech AI Studio program in partnership with International Elite Capital (Fall 2024).*
