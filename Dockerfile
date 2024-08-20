FROM python:3.12-slim

COPY spin_session_setter /opt/spin_session_setter

#We used to use the requirements.txt file however the two versions of the library we need clash with each other,
#so we install them explicitly instead.
#RUN pip install --no-deps -r /opt/spin_session_setter/requirements.txt
RUN pip install stravaweblib==0.0.8
RUN pip install stravalib==2.0

VOLUME /opt/strava_data

ENTRYPOINT ["/opt/spin_session_setter/spin_session_distance_setter.py"]
