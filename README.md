# US Undergraduate Transfer Research Assistant

This tool helps organize and deepen your research for transferring to top US universities.

## Features
- **User Profile Management**: Tracks your current status and interests.
- **School Research**: Structured notes for each target school (Academics, Faculty, Vibe, Transfer Resources).
- **Essay Helper**: Outlining "Why Transfer" essays based on research.

## Usage
1.  **Update Profile**: Edit `data/profile.json` with your details.
2.  **Research**: Use the scripts to gather and organize information.
3.  **Draft**: Generate essay outlines.

## Target Schools
- Duke, Brown, JHU, Northwestern, Columbia, Cornell, UChicago, Dartmouth, UMich, CMU

## Deployment (How to put this online)

### Option 1: Streamlit Community Cloud (Recommended)
This is the easiest and best way to host Streamlit apps.
1.  **Push to GitHub**:
    - Create a new repository on GitHub.
    - Run the following commands in your terminal:
      ```bash
      git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
      git branch -M main
      git push -u origin main
      ```
2.  **Deploy**:
    - Go to [share.streamlit.io](https://share.streamlit.io/).
    - Log in with GitHub.
    - Click "New app".
    - Select your repository, branch (`main`), and main file path (`app.py`).
    - Click "Deploy".

### Option 2: Vercel (Experimental)
Vercel is primarily for static sites and serverless functions, which has limitations for Streamlit (e.g., no WebSocket support, 10s timeout).
If you still want to try:
1.  Install Vercel CLI: `npm i -g vercel`
2.  Run `vercel` in this directory.
3.  **Note**: The app may not function correctly due to Vercel's serverless nature. Streamlit requires a persistent server.

### Prerequisites
- Python 3.9+
- `pip install -r requirements.txt`
