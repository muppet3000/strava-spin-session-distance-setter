FROM python:slim

RUN pip install stravalib stravaweblib

COPY spin_session_setter /opt/spin_session_setter

VOLUME /opt/strava_data

ENTRYPOINT ["/opt/spin_session_setter/spin_session_distance_setter.py"]
