MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "job_scraper"

RESUME_PATH = "resume.txt"
COMPANY_LIST_PATH = "top_50_companies.csv"

JOB_TITLES = ["Full Stack Developer – SDE2", "MERN", "Software Development Engineer II", "Software Engineer II", "SDE2 – MERN Stack"]
LOCATIONS = ["Remote", "WFH", "Hyderabad", "Pune"]  # Priority order

MAX_LINKEDIN_PAGES = 10
MAX_COMPANY_JOBS = 10
MAX_JOBS = 30
MAX_WORKERS = 25

EXPERIENCE = 3
SALARY_THRESHOLD = 10  # Change manually as needed
CHROME_DRIVER_PATH = "chromedriver"

POSTED_TODAY_COLLECTION = "PostedToday"
FILTERED_JOBS_COLLECTION = "FilteredJobs"

LOG_LEVEL = "DEBUG"  # Set to "INFO" for production
