## ai search engine with github things

clone the repository:
 git clone https://github.com/Poushali-02/git-search-ai

Get the API keys
1. FLASK_SECRET_KEY ->generate using secrets from python
2. GEMINI_API_KEY -> get from google ai studio
3. GITHUB_CLIENT_ID -> github oauth application
4. GITHUB_CLIENT_SECRET -> github oauth application

make a .env file and store like this 
FLASK_SECRET_KEY=abcd...
GEMINI_API_KEY=abcd...
GITHUB_CLIENT_ID=abcd...
GITHUB_CLIENT_SECRET=abcd...

activate the virtual environment
venv/Scripts/activate

Install dependencies (in the venv):
pip install -r requirements.txt

Run:
python app.py

Login using github (2 Factor authentication)
Give this command - (for now, requires optimization)
"github issues assigned"
It will return the issues

For other queries it will give detialed information (might be larger than expected, requires optimization) 