from .courses import CodingForCoursesScraper
from .projects import CodingForProjectsScraper


def download_projects(params):
    cf = CodingForProjectsScraper()
    cf.scrap(**params)


def download_courses(params):
    cf = CodingForCoursesScraper()
    cf.scrap(**params)
