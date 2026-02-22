from researcher import SchoolResearcher
from essay_helper import EssayHelper
import json
import os

def run_demo():
    print("Running demo for Cornell University...")
    
    # 1. Load Profile
    with open(os.path.join("data", "profile.json"), 'r') as f:
        profile = json.load(f)
    
    school_name = "Cornell University"
    major = profile.get("track", "ABE")
    interests = "Agricultural Engineering, Research"
    
    # 2. Research
    researcher = SchoolResearcher()
    print(f"Researching {school_name} for major: {major}...")
    data = researcher.research_school(school_name, major, interests)
    
    # 3. Generate Essay Outline
    helper = EssayHelper()
    print(f"Generating essay outline for {school_name}...")
    helper.generate_outline(school_name, profile)
    
    print("\nDemo complete! Check 'research_notes/Cornell_University_notes.md' and 'essays/Cornell_University_outline.md'.")

if __name__ == "__main__":
    run_demo()
