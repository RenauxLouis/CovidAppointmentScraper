import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

CVS_URL = "https://www.cvs.com/immunizations/covid-19-vaccine"
BMC_URL = "https://mychartscheduling.bmc.org/MyChartscheduling/covid19/#/triage"
BMC_SHORTCUT_URL = "https://mychartscheduling.bmc.org/mychartscheduling/SignupAndSchedule/EmbeddedSchedule?id=10033909,10033319,10033364,10033367,10033370,10033706,10033083,10033373&dept=10098252,10098245,10098242,10098243,10098244,10105138,10108801,10098241&vt=2008&lang=en-US"
WALGREENS_URL = "https://www.walgreens.com/findcare/vaccination/covid-19?ban=covid_scheduler_brandstory_main_March2021"

opts = Options()
opts.headless = True
DRIVER = webdriver.Firefox(options=opts)

url_per_website = {
    "cvs": CVS_URL,
    "bmc": BMC_URL,
    "walgreens": WALGREENS_URL,
}

SENDER_EMAIL = "strike.price.notification@gmail.com"
SENDER_PASSWORD = os.environ.get("PASSWORD")

def get_cvs_availability():
    DRIVER.get(CVS_URL)
    DRIVER.find_elements_by_xpath("//*[contains(text(), 'Massachusetts')]")[0].click()
    not_available_messages = DRIVER.find_elements_by_xpath("//*[contains(text(), 'At this time, all appointments in Massachusetts are booked. We’ll add more as they become available. Please check back later.')]")
    return len(not_available_messages) != 1


def get_bmc_availability():
    DRIVER.get(BMC_SHORTCUT_URL)
    timeout = 3
    try:
        element_present = EC.presence_of_element_located((By.ID, "D6F73C26-7627-4948-95EA-2C630C25C5E9_scheduleOpenings_OpeningsData"))
        WebDriverWait(DRIVER, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        not_available_messages = DRIVER.find_elements_by_xpath("//*[contains(text(), 'In the meantime, you can find answers to many questions about COVID-19 vaccines – such as how the vaccine works and information for people with specific health conditions – on BMC.org, which is being updated as we learn more.')]")

    return len(not_available_messages) != 1


def create_secure_connection_and_send_mail(available_website):

    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        send_mail(server, available_website)


def send_mail(server, available_website):

    title = f"{available_website} HAS AVAILABILITY "

    receiver_email = "renauxlouis@gmail.com"
    assert receiver_email.split("@")[1] == "gmail.com"

    msg_root = MIMEMultipart("alternative")
    msg_root["Subject"] = title
    msg_root["From"] = SENDER_EMAIL
    msg_root["To"] = receiver_email
    msg_root.preamble = title

    msg_root.attach(MIMEText(url_per_website[available_website], "plain"))

    server.sendmail(SENDER_EMAIL, receiver_email, msg_root.as_string())


if __name__ == "__main__":

    cvs_has_availability = get_cvs_availability()
    bmc_has_availability = get_bmc_availability()

    if cvs_has_availability:
        create_secure_connection_and_send_mail("cvs")
    if bmc_has_availability:
        create_secure_connection_and_send_mail("bmc")

    DRIVER.close()
