"""
Load testing configuration for BookStore API using Locust
"""

from locust import HttpUser, task, between
import random
import json


class BookStoreUser(HttpUser):
    """Simulates a user interacting with the BookStore API"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts - perform login"""
        self.token = None
        self.user_id = None
        
        # Try to login with test user
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        response = self.client.post("/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
            
            # Set authorization header for future requests
            if self.token:
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
    
    @task(5)
    def view_books(self):
        """View list of books - most common operation"""
        self.client.get("/api/v1/books/")
    
    @task(3)
    def view_book_details(self):
        """View details of a specific book"""
        book_id = random.randint(1, 20)
        self.client.get(f"/api/v1/books/{book_id}")
    
    @task(2)
    def search_books(self):
        """Search for books"""
        search_terms = [
            "python", "javascript", "data", "science", "fiction",
            "programming", "web", "development", "machine", "learning"
        ]
        term = random.choice(search_terms)
        self.client.get(f"/api/v1/books/?q={term}")
    
    @task(2)
    def view_authors(self):
        """View list of authors"""
        self.client.get("/api/v1/authors/")
    
    @task(1)
    def view_author_details(self):
        """View details of a specific author"""
        author_id = random.randint(1, 10)
        self.client.get(f"/api/v1/authors/{author_id}")
    
    @task(1)
    def view_genres(self):
        """View list of genres"""
        self.client.get("/api/v1/genres/")
    
    @task(1)
    def create_book_review(self):
        """Create a book review (authenticated users only)"""
        if not self.token:
            return
        
        book_id = random.randint(1, 20)
        review_data = {
            "rating": random.randint(1, 5),
            "comment": f"Great book! Rating: {random.randint(1, 5)} stars."
        }
        
        self.client.post(
            f"/api/v1/books/{book_id}/reviews",
            json=review_data
        )
    
    @task(1)
    def view_user_profile(self):
        """View user profile (authenticated users only)"""
        if not self.user_id:
            return
        
        self.client.get(f"/api/v1/users/{self.user_id}")
    
    @task(1)
    def manage_reading_list(self):
        """Add book to reading list (authenticated users only)"""
        if not self.token:
            return
        
        book_id = random.randint(1, 20)
        self.client.post(f"/api/v1/reading-lists/books/{book_id}")
    
    @task(10)
    def health_check(self):
        """Health check endpoint - should be fast and reliable"""
        self.client.get("/health")
    
    @task(1)
    def view_metrics(self):
        """View application metrics (if accessible)"""
        self.client.get("/metrics")


class AdminUser(HttpUser):
    """Simulates an admin user with elevated privileges"""
    
    wait_time = between(2, 5)
    weight = 1  # Lower weight - fewer admin users
    
    def on_start(self):
        """Login as admin user"""
        self.token = None
        
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.client.post("/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            
            if self.token:
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
    
    @task(3)
    def create_book(self):
        """Create a new book (admin only)"""
        if not self.token:
            return
        
        book_data = {
            "title": f"Test Book {random.randint(1000, 9999)}",
            "description": "A test book created during load testing",
            "isbn": f"978-{random.randint(1000000000, 9999999999)}",
            "publication_year": random.randint(2000, 2024),
            "author_ids": [random.randint(1, 5)],
            "genre_ids": [random.randint(1, 3)]
        }
        
        self.client.post("/api/v1/books/", json=book_data)
    
    @task(2)
    def create_author(self):
        """Create a new author (admin only)"""
        if not self.token:
            return
        
        author_data = {
            "name": f"Test Author {random.randint(1000, 9999)}",
            "biography": "A test author created during load testing",
            "birth_year": random.randint(1950, 2000)
        }
        
        self.client.post("/api/v1/authors/", json=author_data)
    
    @task(1)
    def update_book(self):
        """Update an existing book (admin only)"""
        if not self.token:
            return
        
        book_id = random.randint(1, 20)
        update_data = {
            "description": f"Updated description {random.randint(1000, 9999)}"
        }
        
        self.client.put(f"/api/v1/books/{book_id}", json=update_data)
    
    @task(1)
    def delete_book(self):
        """Delete a book (admin only) - be careful with this in production!"""
        if not self.token:
            return
        
        # Only delete books with high IDs to avoid deleting important test data
        book_id = random.randint(100, 200)
        self.client.delete(f"/api/v1/books/{book_id}")


class AnonymousUser(HttpUser):
    """Simulates anonymous users (not logged in)"""
    
    wait_time = between(1, 4)
    weight = 3  # Higher weight - more anonymous users
    
    @task(10)
    def browse_books(self):
        """Browse books without authentication"""
        self.client.get("/api/v1/books/")
    
    @task(5)
    def view_book_details(self):
        """View book details without authentication"""
        book_id = random.randint(1, 20)
        self.client.get(f"/api/v1/books/{book_id}")
    
    @task(3)
    def search_books(self):
        """Search books without authentication"""
        search_terms = ["python", "javascript", "science", "fiction"]
        term = random.choice(search_terms)
        self.client.get(f"/api/v1/books/?q={term}")
    
    @task(2)
    def view_authors(self):
        """View authors without authentication"""
        self.client.get("/api/v1/authors/")
    
    @task(1)
    def attempt_protected_action(self):
        """Try to access protected endpoint (should fail)"""
        self.client.post("/api/v1/books/", json={"title": "Unauthorized"})
    
    @task(5)
    def health_check(self):
        """Health check"""
        self.client.get("/health")


# Custom load test scenarios
class StressTestUser(HttpUser):
    """High-intensity user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very short wait times
    weight = 1  # Use sparingly
    
    @task
    def rapid_requests(self):
        """Make rapid requests to test system limits"""
        endpoints = [
            "/health",
            "/api/v1/books/",
            "/api/v1/authors/",
            "/metrics"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)


# Load test configuration
class LoadTestConfig:
    """Configuration for different load test scenarios"""
    
    # Light load - normal usage
    LIGHT_LOAD = {
        "users": 10,
        "spawn_rate": 2,
        "run_time": "5m"
    }
    
    # Medium load - busy periods
    MEDIUM_LOAD = {
        "users": 50,
        "spawn_rate": 5,
        "run_time": "10m"
    }
    
    # Heavy load - peak usage
    HEAVY_LOAD = {
        "users": 100,
        "spawn_rate": 10,
        "run_time": "15m"
    }
    
    # Stress test - system limits
    STRESS_TEST = {
        "users": 200,
        "spawn_rate": 20,
        "run_time": "20m"
    }


# Usage examples:
# locust -f locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=5m --headless
# locust -f locustfile.py --host=https://api.yourdomain.com --users=50 --spawn-rate=5 --run-time=10m --html=report.html