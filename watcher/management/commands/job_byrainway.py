# -*- coding: utf-8 -*-
import re
import requests

from bs4 import BeautifulSoup

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "The tasks processor for the by rw"

    def handle(self, *args, **options):
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

        self.stdout.write('Processing...')

        # TODO specify a client string (browser string)
        session = requests.Session()

        self.stdout.write('Initial request')
        initial_response = session.get(URL_BASE + URL_SCHEDULE)

        initial_soup = BeautifulSoup(initial_response.text, "lxml")
        url = URL_BASE + initial_soup.form['action']
        view_id = initial_soup.select('#com.sun.faces.VIEW')[0]['value']

        form_data = {
            'com.sun.faces.VIEW': view_id,
            '%s:form1' % NAMESPACE: '%s:form1' % NAMESPACE,
            '%s:form1:buttonSearch' % NAMESPACE: 'Продолжить',
            '%s:form1:dob' % NAMESPACE: '20.10.2014',
            '%s:form1:intEndTime' % NAMESPACE: '23',
            '%s:form1:intStartTime' % NAMESPACE: '0',
            '%s:form1:keyErr' % NAMESPACE: '',
            '%s:form1:language1' % NAMESPACE: 'ru',
            '%s:form1:maxDate' % NAMESPACE: '20.11.2014',
            '%s:form1:maxP' % NAMESPACE: '4',
            '%s:form1:minDate' % NAMESPACE: '20.10.2014',
            '%s:form1:onlySchedule' % NAMESPACE: 'true',
            '%s:form1:selectType' % NAMESPACE: '2',
            '%s:form1:textArrStat' % NAMESPACE: 'МИНСК',
            '%s:form1:textArrStatCode' % NAMESPACE: '', # TODO 2100000
            '%s:form1:textDepStat' % NAMESPACE: 'ГОМЕЛЬ-ПАССАЖИРСКИЙ',
            '%s:form1:textDepStatCode' % NAMESPACE: '' #  TODO 2100100
        }

        self.stdout.write('Resulting request')
        response = session.post(url, data=form_data)

        soup = BeautifulSoup(response.text, "lxml")

        details_action = soup.find('form', id='%s:form2' % NAMESPACE)['action']
        svalue = soup.select('#%s:form2:sessionId' % NAMESPACE)[0]['value']
        dview_id = soup.select('#com.sun.faces.VIEW')[0]['value']

        table = soup.find('table',id='%s:form2:tableEx1' % NAMESPACE)

        rows = table.find_all("tr", class_=["rowClass1","grey"])

        trains = {}

        for r in rows:
            tvalue = r.find('input')['value']
            name = r.find('span', style="white-space:nowrap").text.split(" ")[0]
            trains[name] = []

            for k,v in CAR_TYPE:
                regexp = re.compile(v)
                if r.find('span', id=regexp):
                    trains[name].append(k)

            details_data = {
                'com.sun.faces.VIEW': dview_id,
                'rowSelect1': tvalue,
                '%s:form2' % NAMESPACE: '%s:form2' % NAMESPACE,
                '%s:form2:button2' % NAMESPACE: u'Продолжить',
                '%s:form2:sessionId' % NAMESPACE: svalue
            }

            self.stdout.write('Details request')

            details_response = session.post(
                URL_BASE + details_action,
                data=details_data
            )

            dsoup = BeautifulSoup(details_response.text, "lxml")

            for num in xrange(len(trains[name])):
                place_bottom = 0
                place_top = 0
                place_bottom_byside = 0
                place_top_byside = 0

                re_pb = re.compile(
                    r"%s:form1:tableEx1:%d:tableEx2:\d:text21" % (NAMESPACE,num))
                t_pb = dsoup.find_all('span', id=re_pb)
                for i_pb in t_pb:
                    place_bottom += int(i_pb.text)

                re_pt = re.compile(
                    r"%s:form1:tableEx1:%d:tableEx2:\d:text23" % (NAMESPACE,num))
                t_pt = dsoup.find_all('span', id=re_pt)
                for i_pt in t_pt:
                    place_top += int(i_pt.text)

                re_pbs = re.compile(
                    r"%s:form1:tableEx1:%d:tableEx2:\d:text24" % (NAMESPACE,num))
                t_pbs = dsoup.find_all('span', id=re_pbs)
                for i_pbs in t_pbs:
                    place_bottom_byside += int(i_pbs.text)

                re_ptb = re.compile(
                    r"%s:form1:tableEx1:%d:tableEx2:\d:text25" % (NAMESPACE,num))
                t_pts = dsoup.find_all('span', id=re_ptb)
                for i_pts in t_pts:
                    place_top_byside += int(i_pts.text)

                self.stdout.write("%s-%s -> b: %d, t: %d, bs: %d, ts: %d" %\
                    (name, trains[name][num], place_bottom, place_top,
                    place_bottom_byside, place_top_byside))

            # Return back
            self.stdout.write("Return back")
            back_action = dsoup.find('form', id='%s:form1' % NAMESPACE)['action']
            dview_id = dsoup.select('#com.sun.faces.VIEW')[0]['value']

            back_data = {
                'com.sun.faces.VIEW': dview_id,
                '%s:form1:Places' % NAMESPACE: '',
                '%s:form1:link' % NAMESPACE: '',
                '%s:form1:hidePlaces' % NAMESPACE: '0',
                '%s:form1:_id142' % NAMESPACE: u'Назад',
                '%s:form1' % NAMESPACE: '%s:form1' % NAMESPACE,
            }

            response = session.post(
                URL_BASE + back_action,
                data=back_data
            )

            soup = BeautifulSoup(response.text, "lxml")

            details_action = soup.find('form', id='%s:form2' % NAMESPACE)['action']
            svalue = soup.select('#%s:form2:sessionId' % NAMESPACE)[0]['value']
            dview_id = soup.select('#com.sun.faces.VIEW')[0]['value']

        session.close()
