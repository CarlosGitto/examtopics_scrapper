import os

# Exam topics URL
BASE_URL="https://www.examtopics.com"

# Set this value to be the number of pages showed by examtopics
TOTAL_PAGES=os.environ.get("TOTAL_PAGES",21)

# Exam endpoint
ENDPOINT=os.environ.get("EXAM_ENDPOINT","/exams/amazon/aws-certified-solutions-architect-associate-saa-c03/view")

# Exam name to be use in the file name
EXAM_NAME=os.environ.get("EXAM_NAME","SAA-C03")

# Exam types
EXAM_TYPES={
    0:"ONLY_solutions",
    1:"WITH_solutions",
    2:"NO_solutions",
}