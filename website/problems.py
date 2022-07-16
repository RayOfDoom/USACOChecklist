import copy
import random
import time, json, threading

from . import db, app, socketio
from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from .models import ChecklistEntry, ProblemCase, Problem, User
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, TimeoutException

problems = Blueprint('problems', __name__)

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

syncing_threads = {}


# https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
class SyncingThread(threading.Thread):
    def __init__(self, uname, password):
        self.uname = uname
        self.password = password
        self.progress = 5
        self.app = app.app_context()
        self.id = copy.copy(current_user.id)
        self.uuid = str(copy.copy(current_user.extras.unique_key))
        super().__init__()

    def run(self):
        with self.app:
            socketio.emit(self.uuid, {'progress': self.progress, 'message': 'Logging in...', 'type': 'progress-bar-animated'}, json=True)
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            driver.get('http://www.usaco.org/index.php')
            driver.find_element(By.XPATH, '//*[@id="login"]/div[2]/input').send_keys(self.uname)
            driver.find_element(By.XPATH, '//*[@id="login"]/div[3]/input').send_keys(self.password)
            driver.find_element(By.XPATH, '//*[@id="login"]/div[3]/input').send_keys(Keys.RETURN)
            driver.refresh()
            time.sleep(3)

            try:
                driver.find_element(By.XPATH, '//*[@id="login"]')
                driver.quit()
                socketio.emit(self.uuid, {'progress': self.progress, 'message': 'Incorrect login credentials. Try again.', 'type': 'bg-danger'}, json=True)
                return
            except NoSuchElementException:
                pass

            self.progress = 10
            socketio.emit(self.uuid, {'progress': self.progress, 'message': 'Logged in.'}, json=True)

            problem_list = Problem.query.all()
            problem_cnt = 0
            problem_total = len(problem_list)
            for problem in problem_list:
                self.progress = 10 + ((problem_cnt / problem_total) * 90)
                problem_cnt += 1
                socketio.emit(self.uuid, {'progress': self.progress, 'message': 'Fetching ' + problem.name, 'type': 'progress-bar-animated'}, json=True)

                url = 'http://www.usaco.org/index.php?page=viewproblem2&cpid=' + str(problem.pid)
                driver.get(url)

                status = driver.find_element(By.XPATH, '//*[@id="last-status"]/p[1]').get_attribute('innerText')
                if status == "Analysis mode" or status == "Not submitted" or status == "Incorrect answer on sample input case -- details below":
                    continue
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="trial-information"]/a[1]')))
                except TimeoutException:
                    # incorrect sample case
                    continue

                cases = driver.find_elements(By.XPATH, '//*[@id="trial-information"]/a')

                checklist_entry = User.query.filter_by(id=self.id).first().checklist.filter_by(pid=problem.pid).first()
                if not checklist_entry:
                    checklist_entry = ChecklistEntry(user_id=self.id, pid=problem.pid, date=date.today(), progress="attempted")
                    db.session.add(checklist_entry)
                    db.session.commit()

                is_all_correct = True
                case_cnt = 0
                for case in cases:
                    if case_cnt == 0:
                        case_cnt += 1
                        continue
                    correct = case.get_attribute('title') == "Correct answer"
                    if not correct:
                        is_all_correct = False
                    symbol = case.get_attribute('innerText').split('\n')[0][0]

                    try:
                        checklist_entry.cases[case_cnt - 1].correct = correct
                        checklist_entry.cases[case_cnt - 1].symbol = symbol
                    except IndexError:
                        p_case = ProblemCase(entry_id=checklist_entry.entry_id, user_id=self.id, pid=problem.pid, no=case_cnt, correct=correct, symbol=symbol)
                        checklist_entry.cases.append(p_case)

                    case_cnt += 1
                if is_all_correct:
                    checklist_entry.progress = "completed"

            db.session.commit()
        driver.quit()
        socketio.emit(self.uuid, {'progress': self.progress, 'message': 'Completed.', 'type': 'bg-success'}, json=True)


@problems.route('/sync-usaco')
@login_required
def sync_usaco():
    return render_template("sync_usaco.html", user=current_user, user_uuid=current_user.extras.unique_key)


@problems.route('/update-data', methods=['POST'])
@login_required
def update_data():
    global syncing_threads

    uname = request.form.get('uname')
    password = request.form.get('password')

    thread_id = random.randint(0, 10000)
    syncing_threads[thread_id] = SyncingThread(uname, password)
    syncing_threads[thread_id].start()
    return ("/")


@problems.route('/update-problem/<string:probleminfo>', methods=['POST'])
@login_required
def update_problems(probleminfo):
    probleminfo = json.loads(probleminfo)
    pid = probleminfo['pid']
    status = probleminfo['status']

    oldentry = current_user.get_status(pid)
    if oldentry:
        oldentry.date = date.today()
        oldentry.progress = status
    else:
        newentry = ChecklistEntry(user_id=current_user.id, pid=pid, date=date.today(), progress=status)
        db.session.add(newentry)
    db.session.commit()
    return ("/")


@socketio.on('connect debug')
def debug(data):
    pass
