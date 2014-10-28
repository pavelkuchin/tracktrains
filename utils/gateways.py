# -*- coding: utf-8 -*-
import re
import requests
import datetime

from bs4 import BeautifulSoup

from django.conf import settings


class GatewayByRw():
    """
    class-gateway for by rw The responsibility is provide the data like:
    1. Trains availability for given direction and date
    2. Which types of cars are exists
    3. Which types of seats are exists
    cached that all
    """

    URL_BASE = settings.BYRW_BASE_URL
    URL_SCHEDULE = settings.BYRW_DATA_URL
    NAMESPACE = settings.BYRW_NAMESPACE

    CAR_TYPE = [
        ('VIP',r'%s:form2:tableEx1:\d:text25' % NAMESPACE),
        ('SLE',r'%s:form2:tableEx1:\d:text24' % NAMESPACE),
        ('COM',r'%s:form2:tableEx1:\d:text23' % NAMESPACE),
        ('RB', r'%s:form2:tableEx1:\d:text22' % NAMESPACE),
        ('RS', r'%s:form2:tableEx1:\d:text21' % NAMESPACE),
        ('TC', r'%s:form2:tableEx1:\d:text20' % NAMESPACE)
    ]

    HEADERS = {
        'User-Agent': 'tracktrains user agent 0.1',
        'From': 'webmaster@tracktrains.io'
    }

    def __init__(self):
        # TODO specify a client string (browser string)
        self.session = requests.Session()
        self.response_trains = None

    def __enter__(self):
        return self

    def __request_initial(self):
        """
            The initial request for the main page
        """
        return self.session.get(
            self.URL_BASE + self.URL_SCHEDULE,
            headers=self.HEADERS
        )

    def __request_trains(self, response_initial, departure_point,
            destination_point, departure_date):
        """
            The request for trains list
            @param response_initial - result of the self.request_initial()
            @param departure_point - human readable departure station name
            @param destination_point - human readable destination station name
            @patam departure_date - Python date object with requred departure date
            @return Response from the trains page
        """

        soup = BeautifulSoup(response_initial.text, "lxml")

        url = self.URL_BASE + soup.form['action']
        view_id = soup.select('#com.sun.faces.VIEW')[0]['value']

        max_date = departure_date + datetime.timedelta(days=30)

        str_max_date = max_date.strftime('%d.%m.%Y')
        str_departure_date = departure_date.strftime('%d.%m.%Y')

        data = {
            'com.sun.faces.VIEW': view_id,
            '%s:form1' % self.NAMESPACE: '%s:form1' % self.NAMESPACE,
            '%s:form1:buttonSearch' % self.NAMESPACE: 'Продолжить',
            '%s:form1:dob' % self.NAMESPACE: str_departure_date,
            '%s:form1:intEndTime' % self.NAMESPACE: '23',
            '%s:form1:intStartTime' % self.NAMESPACE: '0',
            '%s:form1:keyErr' % self.NAMESPACE: '',
            '%s:form1:language1' % self.NAMESPACE: 'ru',
            '%s:form1:maxDate' % self.NAMESPACE: str_max_date,
            '%s:form1:maxP' % self.NAMESPACE: '4',
            '%s:form1:minDate' % self.NAMESPACE: str_departure_date,
            '%s:form1:onlySchedule' % self.NAMESPACE: 'true',
            '%s:form1:selectType' % self.NAMESPACE: '2',
            '%s:form1:textArrStat' % self.NAMESPACE: destination_point,
            '%s:form1:textDepStat' % self.NAMESPACE: departure_point,
        }

        return self.session.post(url, data=data, headers=self.HEADERS)

    def __request_details(self, response_trains, details_id):
        """
            Request train details in order to get free seats types
            @param response_trains - result of the request_trains
            @param details_id - The input value that is related to train
            @return Response from train details page
        """

        soup = BeautifulSoup(response_trains.text, "lxml")

        action = soup.find('form', id='%s:form2' % self.NAMESPACE)['action']
        session_id = soup.select('#%s:form2:sessionId' % self.NAMESPACE)[0]['value']
        view_id = soup.select('#com.sun.faces.VIEW')[0]['value']

        data = {
            'com.sun.faces.VIEW': view_id,
            'rowSelect1': details_id,
            '%s:form2' % self.NAMESPACE: '%s:form2' % self.NAMESPACE,
            '%s:form2:button2' % self.NAMESPACE: u'Продолжить',
            '%s:form2:sessionId' % self.NAMESPACE: session_id
        }

        url = self.URL_BASE + action

        return self.session.post(url, data=data, headers=self.HEADERS)

    def __request_back(self, response_details):
        """
            Go back to trains list page
            (We need to do it before every request_details)
            @param response_details - result of the request_details page
            @return The same page as request_trains
        """
        #self.stdout.write("Return back")

        soup = BeautifulSoup(response_details.text, "lxml")

        action = soup.find('form', id='%s:form1' % self.NAMESPACE)['action']
        view_id = soup.select('#com.sun.faces.VIEW')[0]['value']
        url = self.URL_BASE + action

        data = {
            'com.sun.faces.VIEW': view_id,
            '%s:form1:Places' % self.NAMESPACE: '',
            '%s:form1:link' % self.NAMESPACE: '',
            '%s:form1:hidePlaces' % self.NAMESPACE: '0',
            '%s:form1:_id142' % self.NAMESPACE: u'Назад',
            '%s:form1' % self.NAMESPACE: '%s:form1' % self.NAMESPACE,
        }

        return self.session.post(url, data=data, headers=self.HEADERS)

    def get_trains(self, departure_point, destination_point, departure_date):
        """
        Fetching the trains list

        @param departure_point - human readable departure station name
        @param destination_point - human readable destination station name
        @patam departure_date - Python date object with requred departure date
        @return trains list
                ex.
                {
                    u'647\u0411': {
                        'train_id': '...',
                        'types': ['COM', 'RB']
                    },
                    u'707\u0411': {
                        'train_id': '...',
                        'types': ['SLE', 'COM', 'RS']
                    },
                    u'100\u041f': {
                        'train_id': '...',
                        'types': ['COM', 'RB']
                    }
                }
        """
        init = self.__request_initial()
        response_trains = self.__request_trains(
            init, departure_point, destination_point, departure_date)
        self.response_trains = response_trains

        soup = BeautifulSoup(response_trains.text, "lxml")
        table = soup.find('table',id='%s:form2:tableEx1' % self.NAMESPACE)
        if not table:
            return {}
        rows = table.find_all("tr", class_=["rowClass1","grey"])

        trains = {}

        for r in rows:
            name = r.find('span', style="white-space:nowrap").text.split(" ")[0]
            details_id = r.find('input')['value']
            trains[name] = {'types': [], 'train_id': details_id}

            for k,v in self.CAR_TYPE:
                regexp = re.compile(v)
                if r.find('span', id=regexp):
                    trains[name]['types'].append(k)

        return trains

    def get_train_details(self, train_id, train_car_types):
        """
            Fetching the train details
            @param train_id - the train_id from get_trains() call result
            @param train_car_types - the types from get_trains() call
            @return the number of free seats grouped by seat level
                    {"COM": {"B": 0,
                             "T": 10,
                             "BS": 5,
                             "TS": 3},
                     "RB": { "B": 2,
                             "T": 1,
                             "BS": 1,
                             "TS": 2}}
        """
        result = {}

        details = self.__request_details(self.response_trains, train_id)
        soup = BeautifulSoup(details.text, "lxml")

        for num in xrange(len(train_car_types)):
            place_bottom = 0
            place_top = 0
            place_bottom_byside = 0
            place_top_byside = 0

            re_pb = re.compile(
                r"%s:form1:tableEx1:%d:tableEx2:\d:text21" % (self.NAMESPACE,num))
            t_pb = soup.find_all('span', id=re_pb)
            for i_pb in t_pb:
                place_bottom += int(i_pb.text)

            re_pt = re.compile(
                r"%s:form1:tableEx1:%d:tableEx2:\d:text23" % (self.NAMESPACE,num))
            t_pt = soup.find_all('span', id=re_pt)
            for i_pt in t_pt:
                place_top += int(i_pt.text)

            re_pbs = re.compile(
                r"%s:form1:tableEx1:%d:tableEx2:\d:text24" % (self.NAMESPACE,num))
            t_pbs = soup.find_all('span', id=re_pbs)
            for i_pbs in t_pbs:
                place_bottom_byside += int(i_pbs.text)

            re_ptb = re.compile(
                r"%s:form1:tableEx1:%d:tableEx2:\d:text25" % (self.NAMESPACE,num))
            t_pts = soup.find_all('span', id=re_ptb)
            for i_pts in t_pts:
                place_top_byside += int(i_pts.text)

            result[train_car_types[num]] = {"B": place_bottom,
                                            "T": place_top,
                                            "BS": place_bottom_byside,
                                            "TS": place_top_byside}

        self.response_trains = self.__request_back(details)

        return result

    def __exit__(self, type, value, traceback):
        self.session.close()
