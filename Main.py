from bs4 import BeautifulSoup
import requests
import os

PARSER = "html.parser"


def download_page(url: str, filename: str):
    page = requests.get(url)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page.text)


def read_page(filename: str) -> str:
    with open(filename, encoding="utf-8") as f:
        return f.read()


def get_pages(username: str):
    url = f"https://github.com/{username}"
    download_page(url, "main.html")  # Get Main Page
    download_page(f"{url}?tab=repositories", "repositories.html")


# get_pages("AbdiA3")

mainBody = read_page("main.html")
repositoriesBody = read_page("repositories.html")
repoBody = read_page("aspiod.html")

with open("main.html", encoding="utf-8") as f:
    mainBody = f.read()


def get_name(page: BeautifulSoup) -> str:
    name = page.select_one(".p-name")
    return name.text.strip()


def get_user_name(page: BeautifulSoup) -> str:
    username = page.select_one(".p-nickname")
    return username.text.strip()


def get_contact(page: BeautifulSoup) -> dict[str]:
    v_card = page.select_one("ul.vcard-details")
    city = v_card.select_one("span.p-label").text.strip()
    return {"city": city}


def get_repositories(page: BeautifulSoup) -> list[str]:
    user_repo_list = page.select_one("#user-repositories-list").select("ul li")
    repo_links = [li.select_one("a") for li in user_repo_list]
    for i, link in enumerate(repo_links):
        repo_links[i] = link.text.strip()
    for repo in repo_links:
        # Get repos using and use get_repo_infos() on each repository
        pass
    return repo_links


def get_repo_infos(page: BeautifulSoup) -> dict:
    # """watch_count = page_head.select_one("#repo-notifications-counter").text"""
    fork_count = page.select_one("#repo-network-counter").text
    star_count = page.select_one("#repo-stars-counter-star").text

    layout_sidebar = page.select("div.Layout-sidebar .BorderGrid-cell")
    result = {"fork": fork_count, "stars": star_count}
    for border_grid_cell in layout_sidebar:
        title = border_grid_cell.select_one("h2")
        if not title:
            continue
        title = title.text.strip().lower()
        if title == "about":
            about = border_grid_cell.select_one("p").text.strip()
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


def get_all_infos(username: str) -> dict:
    os.mkdir(username)
    os.chdir(username)
    get_pages(username)

    main_body = read_page("main.html")
    repositories_body = read_page("repositories.html")

    main_soup = BeautifulSoup(main_body, PARSER)
    repositories_soup = BeautifulSoup(repositories_body, PARSER)
    result = {
        "name": get_name(main_soup),
        "username": get_user_name(main_soup),
        "contact": get_contact(main_soup),
        "repositories": get_repositories(repositories_soup),
    }


print(get_name(mainSoup))
print(get_user_name(mainSoup))
print(get_contact(mainSoup))
print(get_repositories(repositoriesSoup))
print(get_repo_infos(repoSoup))
