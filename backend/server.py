from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
from datetime import datetime, timedelta
import uuid
import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PromptIA - Apartment Search API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.apartment_search

# Pydantic models
class SearchCriteria(BaseModel):
    location: Optional[str] = None
    property_type: Optional[str] = "appartement"
    rooms: Optional[int] = None
    min_surface: Optional[int] = None
    max_surface: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    furnished: Optional[bool] = None
    charges: Optional[str] = "excluded"
    bedrooms: Optional[int] = None
    floor: Optional[int] = None
    balcony: Optional[bool] = False
    parking: Optional[bool] = False
    pets: Optional[bool] = False

class Listing(BaseModel):
    id: str
    title: str
    price: int
    surface: int
    rooms: int
    bedrooms: Optional[int] = 0
    address: str
    description: str
    images: List[str]
    source: str
    published_at: datetime
    furnished: Optional[bool] = False
    charges: Optional[int] = 0
    floor: Optional[int] = 0
    balcony: Optional[bool] = False
    parking: Optional[bool] = False
    pets: Optional[bool] = False
    external_id: Optional[str] = None
    url: Optional[str] = None

class ScrapingConfig:
    """Configuration for web scraping"""
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]
    
    DELAY_RANGE = (2, 5)  # Random delay between requests
    TIMEOUT = 30
    MAX_RETRIES = 3

class WebScraper:
    """Base class for web scrapers"""
    
    def __init__(self):
        self.session = None
        self.driver = None
    
    def get_random_user_agent(self):
        return random.choice(ScrapingConfig.USER_AGENTS)
    
    def get_selenium_driver(self, headless=True):
        """Initialize Selenium WebDriver with stealth configuration"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={self.get_random_user_agent()}")
        
        # Additional stealth options
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute stealth script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    async def random_delay(self):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(*ScrapingConfig.DELAY_RANGE)
        await asyncio.sleep(delay)

class LeBonCoinScraper(WebScraper):
    """Scraper for LeBonCoin.fr"""
    
    BASE_URL = "https://www.leboncoin.fr"
    
    def build_search_url(self, criteria: SearchCriteria):
        """Build search URL based on criteria"""
        url = f"{self.BASE_URL}/recherche?category=10&real_estate_type=2"  # Location, Appartements
        
        if criteria.location:
            # This would need proper location encoding for LeBonCoin
            url += f"&locations={criteria.location}"
        
        if criteria.min_price:
            url += f"&price={criteria.min_price}-{criteria.max_price or ''}"
        
        if criteria.rooms:
            url += f"&rooms={criteria.rooms}-"
        
        if criteria.min_surface:
            url += f"&square={criteria.min_surface}-{criteria.max_surface or ''}"
        
        return url
    
    async def scrape_listings(self, criteria: SearchCriteria) -> List[Dict]:
        """Scrape listings from LeBonCoin"""
        listings = []
        
        try:
            driver = self.get_selenium_driver()
            search_url = self.build_search_url(criteria)
            
            logger.info(f"Scraping LeBonCoin: {search_url}")
            driver.get(search_url)
            
            # Wait for listings to load
            await asyncio.sleep(3)
            
            # Find listing elements (these selectors would need to be updated based on current HTML structure)
            listing_elements = driver.find_elements(By.CSS_SELECTOR, "[data-qa-id='aditem_container']")
            
            for element in listing_elements[:10]:  # Limit to first 10 for demo
                try:
                    listing = self.parse_listing_element(element)
                    if listing:
                        listings.append(listing)
                        await self.random_delay()
                except Exception as e:
                    logger.error(f"Error parsing listing: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping LeBonCoin: {e}")
            if driver:
                driver.quit()
        
        return listings
    
    def parse_listing_element(self, element) -> Optional[Dict]:
        """Parse individual listing element"""
        try:
            # These selectors would need to be updated based on current LeBonCoin HTML structure
            title_elem = element.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_title']")
            price_elem = element.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_price']")
            location_elem = element.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_location']")
            
            title = title_elem.text.strip()
            price_text = price_elem.text.strip()
            location = location_elem.text.strip()
            
            # Extract price (remove currency and spaces)
            price = int(''.join(filter(str.isdigit, price_text))) if price_text else 0
            
            # Get image URL
            img_elem = element.find_element(By.CSS_SELECTOR, "img")
            image_url = img_elem.get_attribute("src") if img_elem else None
            
            # Get listing URL
            link_elem = element.find_element(By.CSS_SELECTOR, "a")
            listing_url = link_elem.get_attribute("href") if link_elem else None
            
            return {
                "id": str(uuid.uuid4()),
                "title": title,
                "price": price,
                "surface": random.randint(20, 100),  # Would extract from description
                "rooms": random.randint(1, 4),  # Would extract from title/description
                "bedrooms": random.randint(0, 3),
                "address": location,
                "description": title,  # Would get full description from detail page
                "images": [image_url] if image_url else [],
                "source": "LeBonCoin",
                "published_at": datetime.now(),
                "furnished": random.choice([True, False]),
                "charges": random.randint(50, 200),
                "floor": random.randint(0, 6),
                "balcony": random.choice([True, False]),
                "parking": random.choice([True, False]),
                "pets": random.choice([True, False]),
                "url": listing_url
            }
            
        except Exception as e:
            logger.error(f"Error parsing listing element: {e}")
            return None

class SeLogerScraper(WebScraper):
    """Scraper for SeLoger.com"""
    
    BASE_URL = "https://www.seloger.com"
    
    def build_search_url(self, criteria: SearchCriteria):
        """Build search URL for SeLoger"""
        url = f"{self.BASE_URL}/list.htm?types=1&natures=1,2,4"  # Appartement, location
        
        if criteria.location:
            # Would need proper location encoding
            url += f"&places={criteria.location}"
        
        if criteria.min_price and criteria.max_price:
            url += f"&price={criteria.min_price}/{criteria.max_price}"
        elif criteria.min_price:
            url += f"&price={criteria.min_price}/NaN"
        
        if criteria.min_surface and criteria.max_surface:
            url += f"&surface={criteria.min_surface}/{criteria.max_surface}"
        elif criteria.min_surface:
            url += f"&surface={criteria.min_surface}/NaN"
        
        if criteria.rooms:
            url += f"&rooms={criteria.rooms}"
        
        return url
    
    async def scrape_listings(self, criteria: SearchCriteria) -> List[Dict]:
        """Scrape listings from SeLoger"""
        # Similar implementation to LeBonCoin but with SeLoger-specific selectors
        # This is a simplified version for demo purposes
        return [
            {
                "id": str(uuid.uuid4()),
                "title": f"Appartement {random.randint(1, 4)} pièces - SeLoger",
                "price": random.randint(800, 2000),
                "surface": random.randint(25, 80),
                "rooms": random.randint(1, 4),
                "bedrooms": random.randint(0, 3),
                "address": f"750{random.randint(1, 20):02d} Paris, Île-de-France",
                "description": "Bel appartement situé dans un quartier recherché...",
                "images": [f"https://images.unsplash.com/photo-{random.randint(1500000000000, 1700000000000)}?w=400"],
                "source": "SeLoger",
                "published_at": datetime.now() - timedelta(days=random.randint(0, 7)),
                "furnished": random.choice([True, False]),
                "charges": random.randint(50, 200),
                "floor": random.randint(0, 6),
                "balcony": random.choice([True, False]),
                "parking": random.choice([True, False]),
                "pets": random.choice([True, False]),
                "url": f"{self.BASE_URL}/annonces/fake-{uuid.uuid4()}"
            }
            for _ in range(random.randint(2, 5))
        ]

class ScrapingOrchestrator:
    """Orchestrates scraping across multiple sites"""
    
    def __init__(self):
        self.scrapers = {
            "leboncoin": LeBonCoinScraper(),
            "seloger": SeLogerScraper(),
            # Add more scrapers here
        }
    
    async def scrape_all_sources(self, criteria: SearchCriteria) -> List[Dict]:
        """Scrape all sources concurrently"""
        all_listings = []
        
        tasks = []
        for source_name, scraper in self.scrapers.items():
            task = self.scrape_source_with_error_handling(source_name, scraper, criteria)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_listings.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
        
        return all_listings
    
    async def scrape_source_with_error_handling(self, source_name: str, scraper: WebScraper, criteria: SearchCriteria) -> List[Dict]:
        """Scrape a single source with error handling"""
        try:
            logger.info(f"Starting scraping for {source_name}")
            listings = await scraper.scrape_listings(criteria)
            logger.info(f"Scraped {len(listings)} listings from {source_name}")
            return listings
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return []

# Global scraping orchestrator
scraping_orchestrator = ScrapingOrchestrator()

# API Routes
@app.get("/")
async def root():
    return {"message": "PromptIA - Apartment Search API"}

@app.post("/api/search")
async def search_apartments(criteria: SearchCriteria, background_tasks: BackgroundTasks):
    """Search for apartments based on criteria"""
    try:
        logger.info(f"Search request: {criteria}")
        
        # First, try to get cached results from database
        cached_listings = await get_cached_listings(criteria)
        
        if cached_listings:
            logger.info(f"Returning {len(cached_listings)} cached listings")
            return {
                "listings": cached_listings,
                "total": len(cached_listings),
                "cached": True
            }
        
        # If no cached results, start scraping in background and return sample data for demo
        background_tasks.add_task(scrape_and_cache_listings, criteria)
        
        # Return sample data immediately for demo purposes
        sample_listings = generate_sample_listings(criteria)
        
        return {
            "listings": sample_listings,
            "total": len(sample_listings),
            "cached": False,
            "message": "Scraping in progress... Real results will be available shortly."
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/listings/{listing_id}")
async def get_listing_details(listing_id: str):
    """Get detailed information for a specific listing"""
    try:
        listing = await db.listings.find_one({"id": listing_id})
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # Remove MongoDB _id field
        listing.pop("_id", None)
        return listing
        
    except Exception as e:
        logger.error(f"Error fetching listing {listing_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/favorites/{listing_id}")
async def add_to_favorites(listing_id: str):
    """Add listing to favorites"""
    # In a real app, this would be user-specific
    try:
        # Simple implementation - just mark as favorite in database
        await db.favorites.insert_one({
            "listing_id": listing_id,
            "added_at": datetime.now()
        })
        return {"message": "Added to favorites"}
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/favorites/{listing_id}")
async def remove_from_favorites(listing_id: str):
    """Remove listing from favorites"""
    try:
        await db.favorites.delete_one({"listing_id": listing_id})
        return {"message": "Removed from favorites"}
    except Exception as e:
        logger.error(f"Error removing from favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/favorites")
async def get_favorites():
    """Get user's favorite listings"""
    try:
        favorites = []
        async for fav in db.favorites.find():
            listing = await db.listings.find_one({"id": fav["listing_id"]})
            if listing:
                listing.pop("_id", None)
                favorites.append(listing)
        
        return {"favorites": favorites}
    except Exception as e:
        logger.error(f"Error fetching favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def get_cached_listings(criteria: SearchCriteria) -> List[Dict]:
    """Get cached listings from database"""
    try:
        # Simple caching - in production, you'd want more sophisticated cache invalidation
        query = {}
        
        if criteria.location:
            query["address"] = {"$regex": criteria.location, "$options": "i"}
        
        if criteria.min_price or criteria.max_price:
            price_query = {}
            if criteria.min_price:
                price_query["$gte"] = criteria.min_price
            if criteria.max_price:
                price_query["$lte"] = criteria.max_price
            query["price"] = price_query
        
        if criteria.rooms:
            query["rooms"] = {"$gte": criteria.rooms}
        
        if criteria.min_surface or criteria.max_surface:
            surface_query = {}
            if criteria.min_surface:
                surface_query["$gte"] = criteria.min_surface
            if criteria.max_surface:
                surface_query["$lte"] = criteria.max_surface
            query["surface"] = surface_query
        
        listings = []
        async for listing in db.listings.find(query).limit(50):
            listing.pop("_id", None)
            # Convert datetime to string for JSON serialization
            if "published_at" in listing:
                listing["published_at"] = listing["published_at"].isoformat()
            listings.append(listing)
        
        return listings
        
    except Exception as e:
        logger.error(f"Error fetching cached listings: {e}")
        return []

async def scrape_and_cache_listings(criteria: SearchCriteria):
    """Scrape listings and cache them"""
    try:
        logger.info("Starting background scraping task")
        
        # Scrape from all sources
        listings = await scraping_orchestrator.scrape_all_sources(criteria)
        
        # Save to database
        for listing in listings:
            # Check if listing already exists
            existing = await db.listings.find_one({"external_id": listing.get("external_id"), "source": listing["source"]})
            
            if not existing:
                await db.listings.insert_one(listing)
                logger.info(f"Cached new listing: {listing['title']}")
            else:
                # Update existing listing
                await db.listings.update_one(
                    {"external_id": listing.get("external_id"), "source": listing["source"]},
                    {"$set": listing}
                )
                logger.info(f"Updated existing listing: {listing['title']}")
        
        logger.info(f"Scraping completed. Processed {len(listings)} listings.")
        
    except Exception as e:
        logger.error(f"Error in scraping task: {e}")

def generate_sample_listings(criteria: SearchCriteria) -> List[Dict]:
    """Generate sample listings for demo purposes"""
    sample_data = [
        {
            "id": str(uuid.uuid4()),
            "title": "Appartement 2 pièces - Centre Paris",
            "price": 1200,
            "surface": 45,
            "rooms": 2,
            "bedrooms": 1,
            "address": "75001 Paris, Île-de-France",
            "description": "Magnifique appartement au cœur de Paris, proche des transports en commun. Entièrement rénové avec une cuisine équipée moderne.",
            "images": ["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400"],
            "source": "LeBonCoin",
            "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "furnished": True,
            "charges": 150,
            "floor": 3,
            "balcony": True,
            "parking": False,
            "pets": False,
            "url": f"https://leboncoin.fr/fake-{uuid.uuid4()}"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Studio meublé - Quartier Latin",
            "price": 850,
            "surface": 25,
            "rooms": 1,
            "bedrooms": 0,
            "address": "75005 Paris, Île-de-France",
            "description": "Studio lumineux dans le quartier historique du Quartier Latin. Parfait pour étudiant ou jeune professionnel.",
            "images": ["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400"],
            "source": "SeLoger",
            "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "furnished": True,
            "charges": 100,
            "floor": 2,
            "balcony": False,
            "parking": False,
            "pets": True,
            "url": f"https://seloger.com/fake-{uuid.uuid4()}"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Appartement 3 pièces avec terrasse",
            "price": 1800,
            "surface": 70,
            "rooms": 3,
            "bedrooms": 2,
            "address": "92100 Boulogne-Billancourt, Île-de-France",
            "description": "Spacieux appartement familial avec grande terrasse. Parking privé inclus. Quartier résidentiel calme.",
            "images": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400"],
            "source": "Foncia",
            "published_at": (datetime.now() - timedelta(days=0)).isoformat(),
            "furnished": False,
            "charges": 200,
            "floor": 5,
            "balcony": True,
            "parking": True,
            "pets": False,
            "url": f"https://foncia.com/fake-{uuid.uuid4()}"
        }
    ]
    
    # Filter sample data based on criteria
    filtered_listings = []
    for listing in sample_data:
        if criteria.location and criteria.location.lower() not in listing["address"].lower():
            continue
        if criteria.min_price and listing["price"] < criteria.min_price:
            continue
        if criteria.max_price and listing["price"] > criteria.max_price:
            continue
        if criteria.rooms and listing["rooms"] < criteria.rooms:
            continue
        if criteria.min_surface and listing["surface"] < criteria.min_surface:
            continue
        if criteria.max_surface and listing["surface"] > criteria.max_surface:
            continue
        
        filtered_listings.append(listing)
    
    return filtered_listings if filtered_listings else sample_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)