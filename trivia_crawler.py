from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup, Comment
import time
import datetime
import pytz


def main():
    # Main site to view scores.
    url = "https://liveprizetrivia.com/team-score/"

    # Table cell that contains team name.
    table_td_class = 'lpt-trivia-leagues-home-venue'

    driver = init_webdriver(url, table_td_class)

    keys, score_dict = get_team_names(driver, table_td_class)

    get_team_scores(driver, keys, score_dict)

    driver.close()

    real_scores = calc_real_scores(score_dict)

    write_scores_to_file(real_scores)


def init_webdriver(url, table_td_class):
    """Initiate selenium headless browser."""
    my_driver_path = "/mnt/c/Python27/chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(my_driver_path, chrome_options=chrome_options)

    driver.get(url)

    # Wait for javascript on page to load.
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, table_td_class))
    )

    return driver


def get_team_names(driver, table_td_class):
    """Get top 25 tournament team names."""
    html_page = driver.page_source
    html_soup = soup(html_page, 'lxml')

    main_table = html_soup.findAll('td', class_=table_td_class)

    data = {}
    keys = []
    for i, cell in enumerate(main_table):
        value = cell.string

        for char in value:
            if not char.isalpha() and not char.isdigit() and char != " ":
                value = value.replace(char, "")

        data[value] = []
        keys.append(value)

    return keys, data


def get_team_scores(driver, keys, score_dict):
    """Get top 25 team scores."""
    table_td_class = 'lpt-trivia-leagues-row'

    # Ensure main table is populated.
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, table_td_class))
    )

    # Get scores of all teams.
    for i in range(len(score_dict)):
        driver.implicitly_wait(60)

        # Click on main table cell to open modal view of scores.
        team = driver.find_elements_by_class_name(table_td_class)
        team[i].click()

        # Wait for modal to populate.
        rows = []
        while len(rows) < 3:
            html_page = driver.page_source
            html_soup = soup(html_page, 'lxml')

            table = html_soup.find('table', class_='table table-striped')
            rows = table.findChildren(['tr'])

        # Add scores to dictionary.
        for row in rows:
            cells = row.findChildren('td')

            for cell in cells:
                value = cell.string

                if value is not None and value.isdigit():
                    score_dict[keys[i]].append(int(value))

        driver.implicitly_wait(60)

        # Click close button of modal to return to main table.
        button_xpath = ("//div[@class='modal-footer']//button[@class='btn "
                        "btn-default btn-lg']")

        close_button = driver.find_element_by_xpath(button_xpath)
        close_button.click()

        time.sleep(1)


def calc_real_scores(score_dict):
    """Take best scores from teams limited to the number of 3 Dog Night
    Posted Scores.
    """
    my_team_name = "3 Dog Night"
    num_scores = len(score_dict[my_team_name])

    real_scores = {}
    for key in score_dict:
        scores = score_dict[key]

        scores.sort()

        scores = scores[::-1]

        total_score = 0
        i = 0
        while i < num_scores and i < len(scores):
            total_score += scores[i]
            i += 1

        real_scores[key] = total_score

    # Create sorte list of tuples (team_name, score)
    sorted_real_scores = sorted(real_scores.items(), key=lambda kv: kv[1])
    sorted_real_scores = sorted_real_scores[::-1]

    return sorted_real_scores


def write_scores_to_file(scores):
    """Writes totals and team name to txt file."""
    with open('score_file.txt', 'w+') as f:
        for team in scores:
            f.write("Name: " + team[0] + "\n")
            f.write("Score: " + str(team[1]) + "\n")

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        pst_now = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
        f.write("Date: " + str(pst_now) + "\n")


if __name__ == "__main__":
    main()
