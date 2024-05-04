from pathlib import Path
import shutil, os, tempfile
from git import Repo, Actor
from google.cloud import secretmanager
from google.oauth2 import service_account
from datetime import date, datetime, timedelta
from letters import letters

project_id, secret_name, version = "gcp-personal-360619", "gh-contributions-gizmo-token", "latest"  # Secrets Manager
repo_name, user = "gh-contributions-gizmo", "micoloth"  # Repo to commit to
username = "Mike Tasca"
file_name = "file.txt"

START_DATE = date(2024, 4, 14)
TEXT = "Hello World! <3 I'm Mike Tasca. I made Ket. Check my stuff."  # This will last a few years...  # TEXT = "abcdefghijklmnopqrstuvwxyz0123456789.,!?:;<'"

gcp_cred_json ="gcp-personal-360619-cd3798141fe6.json"  # See Credentials to run it locally
gcp_credentials = service_account.Credentials.from_service_account_file(gcp_cred_json) if Path(gcp_cred_json).is_file() else None

def get_gh_token(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient(credentials=gcp_credentials)
    name = client.secret_version_path(project_id, secret_id, version_id)
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

def get_git_email():
    """Email is saved in an Env var associated to the Function, it's a pretty naive attempt at obfuscating an info which is public anyway"""
    return os.environ.get("EMAIL")

def clone_repo(local_folder, user, repo_name, token):
    repo_url = f"https://{user}:{token}@github.com/{user}/{repo_name}.git"    
    if os.path.exists(local_folder):  
        shutil.rmtree(local_folder)  # Remove the local folder if it already exists:
    repo = Repo.clone_from(repo_url, local_folder)
    return repo

def make_commit(local_folder, file_name, repo, email, commit_date):
    with open(local_folder + "/" + file_name, "a") as f:
        f.write("a")  # Append a character "a" to the file
    repo.index.add([file_name])
    author, commit_date = Actor(username, email), commit_date.strftime("%Y-%m-%d") + " 12:00:00"
    repo.index.commit("commit " + commit_date, author=author, committer=author, author_date=commit_date, commit_date=commit_date)
    repo.remote(name='origin').push()

def create_fake_directory():
    temp_dir = tempfile.TemporaryDirectory()
    return temp_dir.name

def render_text(text):
    """ This function will take a string of text, and render it in a as binary patches with a heigth of 7 pixels, representing the letters. Width can be as narrow as 1 (for the i) and as wide as 5 (for the w), but usually I think 4 is ok
        final_patch will be a list of COLUMNS. Every elem in final_patch will be a list of 7 elements. So scan the text accordingly:
    """
    final_patch = []
    for letter in text.lower():
        if letter in letters:
            width = len(letters[letter][0])
            for i in range(width):
                final_patch.append([row[i] for row in letters[letter]])
            final_patch.append([0 for _ in range(7)]) # Append an empty column:
    return final_patch

def create_png(letters):
    """Create a PNG image from the text, using the patches:"""
    import numpy as np, matplotlib.pyplot as plt, matplotlib.cm as cm, matplotlib.colors as mcolors
    patch = 1 - np.array(letters).T  # Transpose the patch, and also invert 1 with 0
    fig, ax = plt.subplots()
    ax.imshow(patch, cmap=cm.gray, norm=mcolors.Normalize(vmin=0, vmax=1))  # Now create the image
    ax.axis("off")
    plt.savefig("rendered_text.png"); plt.close()

def get_week_number(date_, start_date = None):
    """ Given a date, returns the week number within that year, OR since start_date, where week 1 is the first week partially included in the year or since start_date
        IMPORTANT: week MUST be considered as starting on SUNDAY, ie Sunday is the first day of the week. The week number will be ZERO INDEXED
    """
    first_day = start_date or date(date_.year, 1, 1)
    first_weekday = first_day.weekday()
    while first_weekday != 6:  # Get the first SUNDAY of the year
        first_day += timedelta(days=1)
    return (date_ - first_day).days // 7 + (1 if first_weekday != 6 else 0)

def get_week_day(date_):
    """ Given a date, returns the day of the week, where Sunday is 0 """
    return (date_.weekday() + 1) % 7  # weekday() returns Monday at 0.  # Convert to Sunday at 0

def main(arg):
    try:
        date_today = datetime.now().date()
        week, weekday = get_week_number(date_today, start_date=START_DATE), get_week_day(date_today)
        patch = render_text(TEXT)  # create_png(patch)
        if week<len(patch) and patch[week][weekday] == 1:
            local_folder = create_fake_directory()
            email, token = get_git_email(), get_gh_token(project_id, secret_name, version)
            repo = clone_repo(local_folder, user, repo_name, token)
            for _ in range(1):  
                make_commit(local_folder, file_name, repo, email, date_today)
            return "Success"
        else:
            return "No commit today"
    except Exception as e:
        return str(e)






# local_folder = create_fake_directory()
# token = get_gh_token(project_id, secret_name, version)
# repo = clone_repo(local_folder, user, repo_name, token)
# email = "mic.tasca@gmail.com"  # get_git_email()

# patch = render_text("llo world ⬜")  # create_png(patch)
# len(patch)
# date_ = BACKFILL_START = date(2023, 5, 14)
# while date_ <= datetime.strptime('2024-03-23', "%Y-%m-%d").date():
#     week, weekday = get_week_number(date_, start_date=BACKFILL_START), get_week_day(date_)
#     print(date_, week, weekday)
#     if week<len(patch) and patch[week][weekday] == 1:
#         make_commit(local_folder, file_name, repo, email, date_)
#     date_ += timedelta(days=1)