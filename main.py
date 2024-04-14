
import os
import shutil
import tempfile
import datetime
from pathlib import Path
from datetime import date
from git import Repo, Actor
from google.cloud import secretmanager
from google.oauth2 import service_account

from patches import patches


gcp_cred_json = "gcp-personal-360619-6095cdc43f13.json"  # See credentials_and_secrets
project_id = "gcp-personal-360619"
secret_name = "gh-contributions-gizmo-token"
version = "latest"

user = "micoloth"
repo_name = "gh-contributions-gizmo"
file_name = "file.txt"
username = "Mike Tasca"

START_DATE = date(2024, 4, 14)

TEXT = "Hello World! <3 I'm Mike Tasca. I made Ket. Check my stuff."  # This will last a few years...
# TEXT = "abcdefghijklmnopqrstuvwxyz0123456789.,!?:;<'"


gcp_credentials = service_account.Credentials.from_service_account_file(gcp_cred_json) if Path(gcp_cred_json).is_file() else None


def get_gh_token(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient(credentials=gcp_credentials)
    name = client.secret_version_path(project_id, secret_id, version_id)
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')


def get_git_email():
    """Email is saved in an Env var associated to the Function, it's a pretty naive attempt at obfuscating an info which is public anyway
    """
    return os.environ.get("EMAIL")


def make_commit(local_folder, email, user, repo_name, token):

    repo_url = f"https://{user}:{token}@github.com/{user}/{repo_name}.git"

    file_path = local_folder + "/" + file_name
    # % [
    # Remove the local folder if it already exists:
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
    repo = Repo.clone_from(repo_url, local_folder)
    # % ]

    # Append a character "a" to the file and save back:
    with open(file_path, "a") as f:
        f.write("a")

    repo.index.add([file_name])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    author = Actor(username, email)
    repo.index.commit("commit " + today, author=author, committer=author)
    origin = repo.remote(name='origin')
    origin.push()


def create_fake_directory():
    temp_dir = tempfile.TemporaryDirectory()
    return temp_dir.name


def render_text(text):
    """ This function will take a string of text, and render it in a as binary patches with a heigth of 7 pixels, representing the letters. Width can be as narrow as 1 (for the i) and as wide as 5 (for the w), but usually I think 4 is ok
        final_patch will be a list of COLUMNS. Every elem in final_patch will be a list of 7 elements. So scan the text accordingly:
    """
    final_patch = []
    for letter in text.lower():
        if letter in patches:
            width = len(patches[letter][0])
            for i in range(width):
                final_patch.append([row[i] for row in patches[letter]])
            # Append an empty column:
            final_patch.append([0 for _ in range(7)])

    return final_patch


def create_png(patches):
    """Create a PNG image from the text, using the patches:
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors

    img_name = "rendered_text.png"
    # Transpose the patch, and also invert 1 with 0:
    patch = np.array(patches).T
    patch = 1 - patch
    # Now create the image:
    fig, ax = plt.subplots()
    ax.imshow(patch, cmap=cm.gray, norm=mcolors.Normalize(vmin=0, vmax=1))
    ax.axis("off")
    plt.savefig(img_name)
    plt.close()



def get_week_number(date, start_date = None):
    """ Given a date, returns the week number within that year, OR since start_date, where week 1 is the first week partially included in the year or since start_date
        IMPORTANT: week MUST be considered as starting on SUNDAY, ie Sunday is the first day of the week
        The week number will be ZERO INDEXED
    """
    first_day = start_date or datetime.date(date.year, 1, 1)
    first_weekday = first_day.weekday()
    # Get the first SUNDAY of the year:
    while first_day.weekday() != 6:
        first_day += datetime.timedelta(days=1)
    weeks = (date - first_day).days // 7 + (1 if first_weekday != 6 else 0)
    return weeks


def get_week_day(date):
    """ Given a date, returns the day of the week, where Sunday is 0
    """
    day = date.weekday()  # Monday is 0
    return (day + 1) % 7  # Convert to Sunday is 0


def main(arg):
    try:
        date_today = datetime.datetime.now().date()
        week, weekday = get_week_number(date_today, start_date=START_DATE), get_week_day(date_today)
        patch = render_text(TEXT)  # create_png(patch)
        if patch[week][weekday] == 1:
            local_folder = create_fake_directory()
            token = get_gh_token(project_id, secret_name, version)
            email = get_git_email()
            make_commit(local_folder, email, user, repo_name, token)
            return "Success"
        else:
            return "No commit today"

    except Exception as e:
        return str(e)
