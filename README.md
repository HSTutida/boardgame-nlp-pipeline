# boardgame-nlp-pipeline
An automated data pipeline for mining, processing, and analyzing board game reviews using Python, Selenium, Pandas, and Large Language Models.

About The Project
Welcome to the codebase of my MBA thesis in Data Science & Analytics. This project demonstrates a complete, end-to-end data pipeline designed to extract, process, and analyze unstructured text data from the world's largest board game forum (BoardGameGeek).

By leveraging Python, Selenium, and Large Language Models (LLMs), this repository implements an Aspect-Based Sentiment Analysis (ABSA) framework. It automatically mines user reviews and categorizes sentiments across specific game dimensions (such as Rules, Components, and Replayability).

Why it matters: > This project showcases my ability to solve real-world analytical problems by:

Architecting robust, stealth-enabled web scrapers to gather multimodal data.

Engineering data pipelines to clean, merge, and structure complex datasets using Pandas.

Applying advanced NLP techniques to transform massive amounts of qualitative text into actionable, structured insights.

## 📊 BoardGameGeek (BGG) Data Miner

### Overview
This repository contains an automated data extraction pipeline designed to mine unstructured text data (user reviews and forum discussions) from BoardGameGeek (BGG). Built with Python and Selenium WebDriver, the script navigates complex web hierarchies to build a dataset for Natural Language Processing (NLP) and Sentiment Analysis.

### 🚀 Key Features
* **Stealth Automation:** Implements headless browsing and WebDriver cloaking techniques (e.g., removing `AutomationControlled` flags, modifying user agents) to bypass basic bot-detection systems and ensure uninterrupted data collection.
* **Dynamic Pagination & Scraping:** Automatically navigates BGG's browse pages to dynamically gather target Game IDs and URLs without relying on static lists.
* **Targeted Forum Mining:** Filters and accesses the "Hot/Top" forum threads for each game, programmatically waiting for DOM elements to load before extracting titles and full-length review texts.
* **Fault-Tolerant Data Engineering:** Processes data iteratively and writes to independent CSV files per game (`reviews_[game_slug].csv`). This micro-batching approach prevents data loss in the event of a network timeout or crash during long extraction runs.
* **Polite Scraping Architecture:** Integrates polite delays (`time.sleep`) to respect the target server's load limits.

### 🛠️ Tech Stack
* **Language:** Python 3.x
* **Browser Automation:** Selenium WebDriver
* **Driver Management:** `webdriver_manager` (for automated Chrome binary synchronization)
* **Data I/O:** Python native `csv` module

### 💡 Why this matters (For Recruiters)
This script demonstrates strong proficiency in **Data Engineering** and **Web Scraping**. It highlights the ability to handle messy, real-world data collection challenges such as dynamic JavaScript rendering, explicit waits, bot mitigation, and structured data storage—all essential first steps in any robust Machine Learning or Data Science pipeline.

## 🤖 LLM-Powered Aspect-Based Sentiment Analysis (ABSA)

### Overview
This repository module leverages Large Language Models (LLMs)—specifically Google's Gemini API—to extract deep, categorical insights from unstructured board game reviews. Instead of a simple "positive/negative" classification, this script performs **Aspect-Based Sentiment Analysis (ABSA)**, identifying specific dimensions of a game (e.g., Rules, Components, Replayability) and analyzing the user's sentiment toward each individual aspect.

### 🚀 Key Features
* **Advanced Prompt Engineering:** Utilizes strict system instructions to define an expert computational linguist persona, constraining the LLM to a predefined taxonomy of 6 game aspects and 3 sentiment polarities.
* **Deterministic JSON Generation:** Configures the LLM with a low temperature (`0.1`) and enforces `application/json` output schemas. This guarantees that the generative model returns consistently parsable, highly structured data without hallucinations or markdown formatting.
* **Robust Data Handling:** Uses `pandas` to load, clean, and iterate through scraped CSV data, including exception handling and dummy-dataset fallbacks for missing files.
* **API Rate-Limit Management:** Implements automated pausing (`time.sleep`) and error-catching (`try/except`) within the processing loop to ensure reliable, uninterrupted API calls over large datasets.
* **Hugging Face Ready:** Exports the final annotated dataset as a properly indented JSON file, structured specifically for downstream ML tasks or uploading to the Hugging Face Hub.

### 🛠️ Tech Stack
* **Generative AI:** Google Gemini API (`gemini-2.5-pro`)
* **Data Engineering:** Python, Pandas, JSON
* **NLP Techniques:** Aspect-Based Sentiment Analysis (ABSA), Zero-Shot Classification, Structured Output Generation


