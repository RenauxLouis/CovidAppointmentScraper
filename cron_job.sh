#!/bin/bash
export PASSWORD="your_password"
export PATH=$PATH:/usr/local/bin && /usr/local/bin/python3 /Users/louisrenaux/CovidAppointmentScraper/scrape_covid_appointment_page.py >> ~/cron.log 2>&1
