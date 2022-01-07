FROM python:3.9-slim
#NOTE: Doesn't work with 3.10 for some reason (mis-match with html5lib)

COPY spin_session_setter /opt/spin_session_setter

RUN pip install -r /opt/spin_session_setter/requirements.txt

VOLUME /opt/strava_data

ENTRYPOINT ["/opt/spin_session_setter/spin_session_distance_setter.py"]
