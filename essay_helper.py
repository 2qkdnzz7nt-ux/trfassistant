import json
import os

class EssayHelper:
    def __init__(self, data_dir="research_notes", output_dir="essays"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def load_research(self, school_name):
        filename = os.path.join(self.data_dir, f"{school_name.replace(' ', '_')}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def generate_outline(self, school_name, user_profile, research_data=None):
        # Use provided research data or load it
        data = research_data if research_data else self.load_research(school_name)
        
        if not data:
            print(f"No research found for {school_name}. Please run research first.")
            return "Error: No research data found."

        outline_path = os.path.join(self.output_dir, f"{school_name.replace(' ', '_')}_outline.md")
        
        # Extract profile info
        current_school = user_profile.get("current_school", "Current School")
        current_major = user_profile.get("track", "Current Major")
        interests = ", ".join(user_profile.get("interests", []))
        
        outline_content = []
        outline_content.append(f"# Why Transfer Essay Outline: {school_name}\n")
        
        # Introduction
        outline_content.append("## 1. Introduction")
        outline_content.append(f"- **Hook**: Start with your current academic journey at {current_school} ({current_major}).")
        outline_content.append("- **The Pivot**: Explain why you are looking to transfer. Mention specific academic needs not fully met currently.")
        outline_content.append(f"- **Thesis**: State clearly why {school_name} is the perfect next step for your goals ({interests}).\n")
        
        # Academic Fit
        outline_content.append("## 2. Academic Fit (The 'Why Here' - Part 1)")
        outline_content.append(f"- Focus on the specific major/department at {school_name}.")
        outline_content.append("- **Key Resources found in research**:")
        # Map new keys: department_research
        academics = data.get("sections", {}).get("department_research", [])
        for item in academics[:3]:
            outline_content.append(f"  - Mention something about: [{item.get('title')}]({item.get('href')})")
        outline_content.append("- Discuss specific courses or curriculum features that excite you.\n")
        
        # Faculty & Research
        outline_content.append("## 3. Faculty & Research Interests")
        outline_content.append(f"- Identify 1-2 professors whose work aligns with your interests: {interests}.")
        faculty = data.get("sections", {}).get("faculty", [])
        for item in faculty[:3]:
             outline_content.append(f"  - Potential mention: [{item.get('title')}]({item.get('href')})")
        outline_content.append("- Explain how you would contribute to their research or learn from them.\n")

        # Campus Community -> Pivot to Research Community/Labs
        outline_content.append("## 4. Research Community & Labs")
        outline_content.append("- Describe how you will contribute to the research community.")
        # Map new keys: labs_and_centers or undergrad_research
        labs = data.get("sections", {}).get("labs_and_centers", [])
        for item in labs[:3]:
             outline_content.append(f"  - Potential lab/center: [{item.get('title')}]({item.get('href')})")
        outline_content.append(f"- Connect this to your current research interests.\n")

        # Conclusion
        outline_content.append("## 5. Conclusion")
        outline_content.append("- Summarize your main reasons for transferring.")
        outline_content.append(f"- Reiterate your enthusiasm for {school_name} and your readiness to succeed there.")
        
        final_outline = "\n".join(outline_content)
        
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(final_outline)
            
        print(f"Essay outline generated at {outline_path}")
        return final_outline

if __name__ == "__main__":
    # Test
    helper = EssayHelper()
    # Mock profile for test
    profile = {"current_school": "UIUC", "major": "ACES"} 
    helper.generate_outline("Cornell University", profile)
