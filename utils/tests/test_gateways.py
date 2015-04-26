# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase

from utils.gateways import GatewayByRw


class GatewaysTest(TestCase):
    """
    Tests for By Rw gateway,
    !!! Caution, tests can be unstable because 3th party resource is involved
    """
    def test_gatewaybyrw(self):
        with GatewayByRw() as gw:
            departure_point = "HOMIEĹ PASAŽYRSKI"
            destination_point = "MINSK"
            departure_date = datetime.datetime.now() + datetime.timedelta(days=5)
            trains = gw.get_trains(
                departure_point,
                destination_point,
                departure_date
            )

            self.assertIsNotNone(trains)
            self.assertNotEqual(trains, 0)

            for k,v in trains.items():
                details = gw.get_train_details(
                    v['train_id'],
                    v['types'][0]
                )

                self.assertIsNotNone(details)
                self.assertNotEqual(details, 0)

    def test_get_station(self):
        with GatewayByRw() as gw:
            result = gw.find_station("MINSK")

            self.assertEqual(result[0]['code'], u"2100000")
            self.assertEqual(result[0]['name'], u"MINSK")
            self.assertEqual(result[0]['full_name'], u"MINSK, BELARUS")

            result = gw.find_station("HOMIEĹ")

            self.assertEqual(result[0]['code'], u"2100100")
            self.assertEqual(result[0]['name'], u"HOMIEĹ PASAŽYRSKI")
            self.assertEqual(result[0]['full_name'], u"HOMIEĹ PASAŽYRSKI, BELARUS")
