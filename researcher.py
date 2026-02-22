import json
import os
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import re

class SchoolResearcher:
    # Mapping of school names to their official domains
    SCHOOL_DOMAINS = {
        "Duke University": "duke.edu",
        "Brown University": "brown.edu",
        "Johns Hopkins University (JHU)": "jhu.edu",
        "Northwestern University": "northwestern.edu",
        "Columbia University": "columbia.edu",
        "Cornell University": "cornell.edu",
        "University of Chicago (UChicago)": "uchicago.edu",
        "Dartmouth College": "dartmouth.edu",
        "University of Michigan (UMich)": "umich.edu",
        "Carnegie Mellon University (CMU)": "cmu.edu"
    }

    def __init__(self, data_dir="research_notes"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
    def fetch_page_content(self, url, timeout=10):
        """Fetches and extracts text content from a URL."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                # Truncate to avoid overly massive blobs, but keep enough for context
                return text[:2000] + "..." if len(text) > 2000 else text
        except Exception as e:
            # print(f"Failed to fetch {url}: {e}") # Silent fail to keep logs clean
            pass
        return None

    def search_yahoo(self, query, max_results=5):
        """
        Performs a search using Yahoo Search (HTML scraping).
        This is currently the most robust method for this environment.
        """
        url = f"https://search.yahoo.com/search?p={urllib.parse.quote_plus(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        results = []
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Yahoo structure: <div class="algo ...">
                items = soup.find_all('div', class_=lambda x: x and 'algo' in x)
                
                for item in items[:max_results]:
                    link = None
                    title_tag = item.find('h3')
                    if title_tag:
                        link = title_tag.find('a')
                    
                    if not link:
                        # Fallback: find first <a> with href that is not '#' and has some text
                        links = item.find_all('a', href=True)
                        for l in links:
                            if l.get_text(strip=True) and not l['href'].startswith('#') and not l['href'].startswith('javascript'):
                                link = l
                                break
                    
                    if link:
                        title = link.get_text(strip=True)
                        raw_href = link['href']
                        
                        # Clean URL (Yahoo redirects)
                        real_href = raw_href
                        if "RU=" in raw_href:
                            try:
                                start = raw_href.find("RU=") + 3
                                end = raw_href.find("/RK=", start)
                                if end == -1: end = len(raw_href)
                                real_href = urllib.parse.unquote(raw_href[start:end])
                            except:
                                pass
                        
                        # Snippet
                        snippet_tag = item.find('div', class_='compText') or item.find('p', class_='fz-14') or item.find('p', class_='lh-16')
                        snippet = snippet_tag.get_text(strip=True) if snippet_tag else "No snippet found"
                        
                        results.append({
                            "title": title,
                            "href": real_href,
                            "body": snippet
                        })
        except Exception as e:
            print(f"Yahoo Search Error for '{query}': {e}")
            
        return results

    def search(self, query, max_results=5, context=None, fetch_content=False):
        """Performs a search and optionally fetches page content."""
        # Use Yahoo as the primary search engine
        # Add random delay to be polite and avoid some rate limits
        time.sleep(0.5) 
        
        raw_results = self.search_yahoo(query, max_results)
        
        # Fallback: If 0 results and query has 'site:', try without 'site:'
        if not raw_results and "site:" in query:
            print(f"Retrying without site filter: {query}")
            clean_query = re.sub(r'site:\S+', '', query).strip()
            raw_results = self.search_yahoo(clean_query, max_results)
        
        results = []
        for res in raw_results:
            item = {
                "title": res.get("title"),
                "href": res.get("href"),
                "body": res.get("body")
            }
            if context:
                item['title'] = f"[{context}] {item['title']}"
            
            # Deep Dive: Fetch content if requested (e.g. for faculty)
            if fetch_content:
                # Add slight delay before fetch
                time.sleep(0.2)
                content = self.fetch_page_content(item['href'])
                if content:
                    item['extracted_content'] = content
                    # If extracted content is good, use it to augment the body
                    item['body'] = content[:300] + "..." # Show preview in body
            
            results.append(item)
                    
        return results

    def find_official_department_site(self, school_name, track):
        """Finds the official department/major website."""
        query = f"{school_name} {track} department official website"
        results = self.search_yahoo(query, max_results=1)
        if results:
            return results[0]['href'], results[0]['title']
        return None, None

    def find_department_faculty_page(self, school_name, track):
        """Finds the official department faculty/people directory."""
        query = f"{school_name} {track} department faculty directory"
        results = self.search_yahoo(query, max_results=1)
        if results:
            return results[0]['href'], results[0]['title']
        return None, None

    def find_department_courses_page(self, school_name, track):
        """Finds the official department courses catalog/curriculum page."""
        query = f"{school_name} {track} department courses catalog curriculum"
        results = self.search_yahoo(query, max_results=1)
        if results:
            return results[0]['href'], results[0]['title']
        return None, None

    def find_department_research_page(self, school_name, track):
        """Finds the official department research/labs page."""
        query = f"{school_name} {track} department research areas labs"
        results = self.search_yahoo(query, max_results=1)
        if results:
            return results[0]['href'], results[0]['title']
        return None, None

    def scrape_research_content(self, url):
        """Fetches and extracts research-specific content from a URL."""
        print(f"Scraping research content from {url}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find a specific "Research" link in the nav if we are on the main page
                # This is a heuristic: look for links with text "Research"
                research_url = None
                for a in soup.find_all('a', href=True):
                    if "research" in a.get_text().lower() and len(a.get_text()) < 20:
                        # Construct absolute URL
                        href = a['href']
                        if href.startswith('http'):
                            research_url = href
                        elif href.startswith('/'):
                            # Base URL construction
                            parsed_uri = urllib.parse.urlparse(url)
                            base = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                            research_url = base + href
                        break
                
                # If we found a research sub-page, scrape that instead
                if research_url and research_url != url:
                    print(f"Found research sub-page: {research_url}")
                    # Recursively fetch the sub-page content
                    return self.fetch_page_content(research_url), research_url
                
                # Otherwise, scrape the current page
                return self.fetch_page_content(url), url
        except Exception as e:
            print(f"Error scraping research page: {e}")
        return None, None

    def research_school(self, school_name, interests, track, status_callback=None):
        """Conducts comprehensive research on a school using parallel execution."""
        print(f"Researching {school_name}...")
        
        research_data = {
            "school_name": school_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sections": {}
        }
        
        # --- NEW FLOW: 1. Official Site -> 2. Research Content -> 3. Summary ---
        
        # 1. Find Official Site
        if status_callback: status_callback("Finding official department website...")
        
        # Helper to find official site
        def get_official_site():
            query = f"{school_name} {track} department official website"
            # Use search_yahoo method from self
            results = self.search_yahoo(query, max_results=1)
            if results:
                return results[0]['href'], results[0]['title']
            return None, None

        official_url, official_title = get_official_site()
        
        if official_url:
            research_data["official_site"] = {"url": official_url, "title": official_title}
            
            # 2. Scrape Research Content
            if status_callback: status_callback(f"Scraping research content from {official_title}...")
            
            # Use scrape_research_content method from self
            research_content_text, research_url = self.scrape_research_content(official_url)
            
            if research_content_text:
                research_data["research_content"] = {
                    "url": research_url,
                    "content": research_content_text
                }
        else:
             # Fallback if no official site found
             research_data["official_site"] = {"url": "#", "title": "Not Found"}
        
        # Keep the parallel search for other details as backup/supplement
        # Determine domain constraint
        domain = self.SCHOOL_DOMAINS.get(school_name)
        site_filter = f" site:{domain}" if domain else ""
        
        # Refined Queries for Essay Writing - FOCUSED ON MAJOR/COLLEGE RESEARCH
        # User requested to remove generic framework and focus on "Intended Major" College Research
        
        tasks = {
            "department_research": (f"{school_name} {track} department research overview", 4, "Dept Research", True),
            "labs_and_centers": (f"{school_name} {track} research laboratories and centers", 4, "Labs & Centers", False),
            "undergrad_research": (f"{school_name} {track} undergraduate research opportunities", 4, "Undergrad Ops", True),
            "research_projects": (f"{school_name} {track} student research projects", 3, "Projects", False)
        }

        # Add specific interest-based faculty searches with Content Fetching
        # Use site: filter for faculty to ensure we get official profiles
        interest_list = [i.strip() for i in interests.split(',') if i.strip()]
        for idx, interest in enumerate(interest_list[:3]): # Limit to top 3 interests
            tasks[f"faculty_interest_{idx}"] = (
                f"{school_name} {track} faculty research {interest}{site_filter}", 
                3, 
                f"Prof. Research ({interest})", 
                True # Enable scraping for professors
            )

        results_map = {}
        
        # Execute searches in parallel
        # Reduce max_workers to avoid hitting Yahoo rate limits too hard
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_key = {
                executor.submit(self.search, query, max_results, context, fetch_content): key 
                for key, (query, max_results, context, fetch_content) in tasks.items()
            }
            
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    data = future.result()
                    results_map[key] = data
                    if status_callback:
                        status_callback(f"Found {len(data)} results for {key}...")
                except Exception as exc:
                    print(f"{key} generated an exception: {exc}")
                    results_map[key] = []

        # Assemble results
        # Group Faculty results together
        faculty_results = []
        for k, v in results_map.items():
            if k.startswith("faculty_interest_"):
                faculty_results.extend(v)
            else:
                research_data["sections"][k] = v
        
        research_data["sections"]["faculty"] = faculty_results
        
        # Add timestamp to extracted content for tracking
        research_data["sections"]["meta"] = {"source": "Yahoo Search (Automated)"}

        return research_data
