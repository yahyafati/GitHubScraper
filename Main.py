from io import StringIO
import json
from bs4 import BeautifulSoup
import requests
import os

PARSER = "html.parser"


def download_page(url: str, filename: str):
    """
    [Debug Only]

    Downloads a url to filename

    Parameters:
        * url (str): url to get

        * filename (str): name of file to save into

    Returns:
        None
    """
    page = requests.get(url)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page.text)


def read_page(filename: str) -> str:
    """
    [Debug Only]

    Reads a file and returns the content of a file.
    Parameter:
        * filename - name of file to read

    Returns:
        Content of file
    """
    with open(filename, encoding="utf-8") as f:
        return f.read()


def get_pages(username: str):
    """
    [Debug Only]

    Download the main and repositories list pages.

    Parameters:
        * username - github username

    Returns:
        None
    """
    url = f"https://github.com/{username}"
    download_page(url, "main.html")  # Get Main Page
    download_page(f"{url}?tab=repositories", "repositories.html")


def get_name(page: BeautifulSoup) -> str:
    """
    Extracts the name of a user from a soup object made from the homepage of a user.
    The page should have been made from the link https://github.com/{username}

    Parameters:
        * page (BeautifulSoup):  object of the profile page of a user

    Returns:
        * str : returns the name of the user on GitHub
    """
    name = page.select_one(".p-name")
    return name.text.strip()


def get_user_name(page: BeautifulSoup) -> str:
    """
    Extracts the username of a user from a soup object made from the homepage of a user.
    The page should have been made from the link https://github.com/{username}

    Parameters:
        * page (BeautifulSoup):  object of the profile page of a user

    Returns:
        * str : returns the username of the user on GitHub
    """
    username = page.select_one(".p-nickname")
    return username.text.strip()


def get_contact(page: BeautifulSoup) -> dict[str]:
    """
    Extracts the contact of a user from a soup object made from the homepage of a user.
    The page should have been made from the link https://github.com/{username}

    Parameters:
        * page (BeautifulSoup):  object of the profile page of a user

    Returns:
        * str : returns the contact of the user on GitHub
    """
    v_card = page.select_one("ul.vcard-details")
    city = v_card.select_one("span.p-label")
    if city:
        city = city.text.strip()
    return {"city": city}


def get_repositories_list(page: BeautifulSoup) -> list[str]:
    """
    Extracts the list of repositories of a user from a soup object made from the repositories of a user.
    The page should have been made from the link https://github.com/{username}?tab=repositories

    Parameters:
        * page (BeautifulSoup):  object of the repository page of a user

    Returns:
        * list[str] : returns the list of repositories' name
    """
    user_repo_list = page.select_one("#user-repositories-list").select("ul li")
    repo_links = [li.select_one("a") for li in user_repo_list]
    for i, link in enumerate(repo_links):
        if not link:
            continue
        repo_links[i] = link.text.strip()
    return repo_links


def get_all_repository_details(username: str, repos: list[str] = None) -> dict:
    """
    Returns a dictionary containing all the repositories of a user and its details

    Parameters:
        * username (str) - username of the user

    Returns:
        * dict[str, Any] - all repositories and its details
    """
    base_url = f"https://github.com/{username}"
    if repos == None:
        page = requests.get(f"{base_url}?tab=repositories")
        soup = BeautifulSoup(page.text, PARSER)
        repos = get_repositories_list(soup)

    result = dict()
    for repo in repos:
        res = requests.get(f"{base_url}/{repo}")
        repo_soup = BeautifulSoup(res.text, PARSER)
        result[repo] = get_repo_details(repo_soup)
    return result


def get_repo_details(page: BeautifulSoup) -> dict:
    """
    Extracts the details of a repository from a soup object made from the page of the repository.
    The page should have been made from the link https://github.com/{username}/{reponame}

    Parameters:
        * page (BeautifulSoup):  object of the repository page of a user

    Returns:
        * dict[str, Any] : returns a dictionary with the details of a repository
    """
    # """watch_count = page_head.select_one("#repo-notifications-counter").text"""
    fork_count = page.select_one("#repo-network-counter").text
    star_count = page.select_one("#repo-stars-counter-star").text

    layout_sidebar = page.select("div.Layout-sidebar .BorderGrid-cell")
    result = {"fork": fork_count, "stars": star_count}
    result["branch"] = get_branch_name(page)
    for border_grid_cell in layout_sidebar:
        title = border_grid_cell.select_one("h2")
        if not title:
            continue
        title = title.text.strip().lower()
        if title == "about":
            about = border_grid_cell.select_one("p")
            if about:
                about = about.text.strip()
            result["about"] = about
            website = border_grid_cell.select_one("div a")
            if website:
                website = website.text.strip()
                result["website"] = website
        elif title == "languages":
            langs_list = border_grid_cell.select_one("ul")
            result["languages"] = []
            for lang_item in langs_list.select("li a"):
                lang = lang_item.find_all("span")[0].text
                percent = lang_item.find_all("span")[1].text
                result["languages"].append((lang, percent))
    return result


def get_branch_name(page: BeautifulSoup) -> str:
    """
    Extracts the name of the branch of a repository from a soup object made from the page of the repository.
    The page should have been made from the link https://github.com/{username}/{reponame}

    Parameters:
        * page (BeautifulSoup):  object of the repository page of a user

    Returns:
        * str : name of the branch that is currently being worked on
    """
    branch_select_menu = page.select_one("#branch-select-menu")
    summary = branch_select_menu.select_one("summary")
    return summary.text.strip()


def get_all_infos(username: str) -> dict[str]:
    """
    Returns a dictionary containing all the data needed on a user.

    Parameters:
        * username (str) - the username of the person

    Returns:
        * dict[str, Any] - all the data on the person
    """
    # os.mkdir(username)
    # os.chdir(username)
    # get_pages(username)
    # main_body = read_page("main.html")
    # repositories_body = read_page("repositories.html")

    url = f"https://github.com/{username}"
    main_body = requests.get(url).text

    main_soup = BeautifulSoup(main_body, PARSER)
    result = {
        "name": get_name(main_soup),
        "username": get_user_name(main_soup),
        "contact": get_contact(main_soup),
        "repositories": get_all_repository_details(username),
    }
    # os.chdir("..")
    return result


def save_as_json(username: str, infos: dict = None):
    """
    Gets all the data on a person based on their username and saves it to as a json file.

    Parameters:
        * username (str) - username of the user being searche. This will be the filename of the file being saved. It will also be used to get all information using get_all_infos(username) when no infos is passed.
        * infos (dict) - a dictionary containing an already extracted information on the data. (Optional)

    Return:
        None
    """
    if infos == None:
        infos = get_all_infos(username)
    with open(f"{username}.json", "w") as f:
        json.dump(infos, f)


def get_json(username: str, infos: dict = None) -> str:
    """
    Gets all the data on a person based on their username and returns it as a json fromatted string.

    Parameters:
        * username (str) - username of the user being searche. This will be the filename of the file being saved. It will also be used to get all information using get_all_infos(username) when no infos is passed.
        * infos (dict) - a dictionary containing an already extracted information on the data. (Optional)

    Return:
        * str - JSON formatted infos
    """
    if infos == None:
        infos = get_all_infos(username)
    return json.dumps(infos)


print(save_as_json("navy87"))
# save_as_json("0xecho")

# repo_page = read_page("aspiod.html")
# soup = BeautifulSoup(repo_page, PARSER)
# print(get_branch_name(soup))
