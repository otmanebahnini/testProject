import requests
import json
import sys
from datetime import datetime
import time

class ApartmentSearchAPITester:
    def __init__(self, base_url="https://6b16581a-755f-4aa3-8e35-51ae9ac6fea2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_search_apartments(self, criteria):
        """Test the search apartments endpoint"""
        success, response = self.run_test(
            "Search Apartments",
            "POST",
            "api/search",
            200,
            data=criteria
        )
        
        if success:
            print(f"Found {len(response.get('listings', []))} listings")
            if 'listings' in response and len(response['listings']) > 0:
                print(f"Sample listing: {response['listings'][0]['title']}")
        
        return success, response.get('listings', [])

    def test_get_listing_details(self, listing_id):
        """Test getting details for a specific listing"""
        success, response = self.run_test(
            f"Get Listing Details (ID: {listing_id})",
            "GET",
            f"api/listings/{listing_id}",
            200
        )
        return success

    def test_add_to_favorites(self, listing_id):
        """Test adding a listing to favorites"""
        success, response = self.run_test(
            f"Add to Favorites (ID: {listing_id})",
            "POST",
            f"api/favorites/{listing_id}",
            200
        )
        return success

    def test_get_favorites(self):
        """Test getting favorite listings"""
        success, response = self.run_test(
            "Get Favorites",
            "GET",
            "api/favorites",
            200
        )
        
        if success:
            favorites = response.get('favorites', [])
            print(f"Found {len(favorites)} favorites")
        
        return success

    def test_remove_from_favorites(self, listing_id):
        """Test removing a listing from favorites"""
        success, response = self.run_test(
            f"Remove from Favorites (ID: {listing_id})",
            "DELETE",
            f"api/favorites/{listing_id}",
            200
        )
        return success

def main():
    # Setup
    tester = ApartmentSearchAPITester()
    
    # Test root endpoint
    if not tester.test_root_endpoint():
        print("❌ Root endpoint test failed, stopping tests")
        return 1
    
    # Test search with various criteria
    search_criteria = {
        "location": "Paris",
        "property_type": "appartement",
        "rooms": 2,
        "min_price": 1000,
        "max_price": 1500,
        "min_surface": 40,
        "max_surface": 80
    }
    
    search_success, listings = tester.test_search_apartments(search_criteria)
    if not search_success:
        print("❌ Search test failed, stopping tests")
        return 1
    
    # If we have listings, test the listing details endpoint
    if listings:
        listing_id = listings[0]['id']
        if not tester.test_get_listing_details(listing_id):
            print("❌ Get listing details test failed")
        
        # Test favorites functionality
        if not tester.test_add_to_favorites(listing_id):
            print("❌ Add to favorites test failed")
        
        if not tester.test_get_favorites():
            print("❌ Get favorites test failed")
        
        if not tester.test_remove_from_favorites(listing_id):
            print("❌ Remove from favorites test failed")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())