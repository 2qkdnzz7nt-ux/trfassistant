import json
import os
from researcher import SchoolResearcher
from essay_helper import EssayHelper

PROFILE_PATH = os.path.join("data", "profile.json")

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_profile(profile):
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profile, f, indent=4)

def main():
    print("Welcome to the US Transfer Research Assistant!")
    profile = load_profile()
    researcher = SchoolResearcher()
    helper = EssayHelper()

    while True:
        print("\n--- Main Menu ---")
        print("1. View/Edit Profile")
        print("2. Research a Target School")
        print("3. Generate Essay Outline")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print("\nCurrent Profile:")
            print(json.dumps(profile, indent=2))
            update = input("Do you want to update interests? (y/n): ")
            if update.lower() == 'y':
                new_interests = input("Enter new interests (comma separated): ")
                profile['interests'] = [i.strip() for i in new_interests.split(',')]
                save_profile(profile)
                print("Profile updated.")
        
        elif choice == '2':
            print("\nTarget Schools:")
            for i, school in enumerate(profile.get('target_schools', [])):
                print(f"{i+1}. {school}")
            
            school_idx = input("Select school number to research (or type name): ")
            try:
                idx = int(school_idx) - 1
                if 0 <= idx < len(profile['target_schools']):
                    school_name = profile['target_schools'][idx]
                else:
                    school_name = school_idx
            except ValueError:
                school_name = school_idx
            
            print(f"Starting research for {school_name}...")
            # Use profile info for targeted search
            major = profile.get('track', 'Undecided')
            interests = ", ".join(profile.get('interests', []))
            
            researcher.research_school(school_name, major, interests)
            print(f"Research completed for {school_name}. Check research_notes/ folder.")

        elif choice == '3':
            school_name = input("Enter school name for essay outline: ")
            helper.generate_outline(school_name, profile)
            print(f"Outline generated in essays/ folder.")

        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
