import json
from pathlib import Path

import requests
from loguru import logger


def refresh(course_id, exercise_id, solutions, token) -> bool:
    logger.info("Refreshing submissions")
    # process = subprocess.run([
    #     'bash',
    #     'fetch_submissions.sh',
    #     # course id
    #     course_id,
    #     # excercise id
    #     exercise_id,
    #     # output directory
    #     solutions,
    #     # token location
    #     token,
    # ])
    returncode = main(solutions, course_id=course_id, exercise_id=exercise_id, token=token)
    # 0 means new data has been copied, so a real refresh
    return returncode == 0


def get(url, token="token"):
    token = Path(token)
    token = token.read_text()
    headers = {"Accept": "application/json", "Authorization": token}
    logger.debug(url)
    resp = requests.get(url, headers=headers)
    return resp.json()


def query(path, base="https://dodona.be/"):
    return get(base + path)


def fetch_correct(course, exercise, page):
    return query(
        f"courses/{course}/activities/{exercise}/submissions/?most_recent_per_user=true&status=correct&page={page}"
    )


def write_submissions(fetched, solutions_path):
    for k, v in fetched.items():
        submission = get(v["url"])
        name = f"solution_{k}.py"
        path = solutions_path / name
        # print(submission.code)
        path.write_text(submission["code"])


def reduced_result(url):
    o = get(url)
    result = json.loads(o["result"])
    try:
        reduced_result = result["groups"][-1]
        del result["groups"]
        result["groups"] = reduced_result
    except KeyError:
        logger.info("Fail for {url}")
    return result


def main(solutions, course_id, exercise_id, max_pages=10, force=False, *args, **kwargs):
    logger.info("Start fetching...")
    solutions = Path(solutions).resolve()
    solutions.mkdir(exist_ok=True)
    new_fetch = []
    fetched = {}
    users = set()
    page = 0
    # loop over all solutions through pagination
    while page == 0 or (len(new_fetch) > 0 and page < max_pages):
        logger.info(f"Page {page}")
        new_fetch = fetch_correct(course_id, exercise_id, page)
        # add new submissions to the set of submissions with user id as key
        for s in new_fetch:
            user_id = str(s["id"])
            users.add(user_id)
            fetched[user_id] = s
        page += 1
    logger.debug(new_fetch)
    logger.debug(fetched)

    # load old submissions
    students_path = solutions / "students.json"
    if students_path.exists():
        with students_path.open("r", encoding="UTF-8") as fh:
            old_students = json.load(fh)
        old_set = set(old_students.keys())
    else:
        old_set = set()

    # set of new submissions
    new_set = set(fetched.keys())

    # difference between old and new submissions
    diff = new_set - old_set
    if diff or force:
        logger.info(f"{len(diff)} new submission(s) detected!")

        if solutions.exists():
            # remove all solutions, but not the previous .json file
            for s in solutions.glob("solution_*.py"):
                s.unlink()

        # extend all fetched submissions with more information
        for v in fetched.values():
            user = get(v["user"])
            # edit in place
            v["user"] = user
            v["result"] = reduced_result(v["url"])

        # update the students.json file with new submissions
        with students_path.open("w", encoding="UTF-8") as fh:
            json.dump(fetched, fh, indent=4)
        write_submissions(fetched, solutions)
        return 0
    else:
        logger.info("No new submissions detected")
        return 1
