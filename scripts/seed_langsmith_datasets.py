import os
from langsmith import Client

# This should be configured with your API keys
# os.environ["LANGCHAIN_API_KEY"] = "..."

def seed_datasets():
    """
    Creates the LangSmith datasets and adds examples to each.
    """
    client = Client()
    
    # Dataset for website content checks
    website_dataset_name = "website-content-checks"
    try:
        website_dataset = client.read_dataset(dataset_name=website_dataset_name)
    except Exception:
        website_dataset = client.create_dataset(dataset_name=website_dataset_name, description="A dataset for verifying website content.")
        
    website_examples = [
        {"url": "https://www.killeentexas.gov/rss.aspx", "label": "verified", "reasons": "Official government website for the City of Killeen."},
        {"url": "https://kdhnews.com/search/?f=rss&t=article&l=50&s=start_time&sd=desc&k%5B%5D=%23topstory", "label": "verified", "reasons": "Reputable local news source."},
        {"url": "https://killeenpdnews.com/feed/", "label": "verified", "reasons": "Official news feed for the Killeen Police Department."},
        {"url": "https://city-of-temple.prowly.com/rss", "label": "verified", "reasons": "Official news feed for the City of Temple."},
        {"url": "https://capitol.texas.gov/MyTLO/RSS/RSSFeeds.aspx?FeedType=TodayBillsFiledHouse", "label": "verified", "reasons": "Official website for the Texas Legislature."},
    ]
    
    for example in website_examples:
        try:
            client.create_example(
                inputs={"url": example["url"]},
                outputs={"label": example["label"], "reasons": example["reasons"], "evidence_links": [example["url"]]},
                dataset_id=website_dataset.id,
            )
        except Exception:
            pass # Example might already exist

    # Dataset for news validation
    news_dataset_name = "news-validation"
    try:
        news_dataset = client.read_dataset(dataset_name=news_dataset_name)
    except Exception:
        news_dataset = client.create_dataset(dataset_name=news_dataset_name, description="A dataset for validating news articles.")
        
    news_examples = [
        {"url": "https://killeenpdnews.com/2026/02/11/killeen-police-identify-and-arrest-murder-suspect-3/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/02/10/killeen-police-investigating-the-murder-of-a-22-year-old-male/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://city-of-temple.prowly.com/446336-temple-police-department-investigates-a-traffic-accident-1-deceased", "label": "verified", "reasons": "Official press release from the Temple Police Department."},
        {"url": "https://city-of-temple.prowly.com/446284-city-of-temple-to-host-5th-annual-black-history-month-ceremony", "label": "verified", "reasons": "Official press release from the City of Temple."},
        # Add more examples here...
        {"url": "https://killeenpdnews.com/2026/01/10/killeen-police-investigate-a-fatality-crash-on-stan-schlueter-loop/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/15/killeen-police-charge-second-suspect-in-fatal-monte-carlo-shooting/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/18/killeen-police-investigate-fatal-shooting-on-illinois-avenue/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/22/killeen-police-identify-deceased-male-from-fatal-shooting/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/26/killeen-police-conduct-a-death-investigation-on-rancier-avenue/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/28/killeen-police-investigate-a-single-vehicle-fatality-on-roy-reynolds/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/01/31/killeen-police-investigating-multi-vehicle-crash-on-interstate-14/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://killeenpdnews.com/2026/02/01/killeen-police-investigating-the-murder-of-a-35-year-old-male/", "label": "verified", "reasons": "Official press release from the Killeen Police Department."},
        {"url": "https://city-of-temple.prowly.com/446125-temple-police-department-investigates-assault-on-a-public-servant-4-injured", "label": "verified", "reasons": "Official press release from the Temple Police Department."},
        {"url": "https://city-of-temple.prowly.com/446140-temple-police-department-investigates-a-traffic-accident-2-injured", "label": "verified", "reasons": "Official press release from the Temple Police Department."},
        {"url": "https://city-of-temple.prowly.com/446338-code-compliance", "label": "verified", "reasons": "Official press release from the City of Temple."},
    ]
    
    for example in news_examples:
        try:
            client.create_example(
                inputs={"url": example["url"]},
                outputs={"label": example["label"], "reasons": example["reasons"], "evidence_links": [example["url"]]},
                dataset_id=news_dataset.id,
            )
        except Exception:
            pass # Example might already exist

    print("Successfully seeded the LangSmith datasets.")

if __name__ == "__main__":
    seed_datasets()
