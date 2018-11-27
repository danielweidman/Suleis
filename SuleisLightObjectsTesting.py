import unittest

from SuleisLightObjects import MainDatabase, User, Section, Strip, Pattern, SolidPattern, TimePattern, SunPattern, DynamicPattern


class TestStringMethods(unittest.TestCase):




    def test_add_user(self): #Test adding a user to the database
        class testUserG:  # use this to simulate the generic user objecg g used in app.py
            def __init__(self, id, first_name, last_name):
                self.id = id
                self.profile = self.profileTest(first_name, last_name)

            class profileTest:
                def __init__(self, first_name, last_name):
                    self.firstName = first_name
                    self.lastName = last_name

        self.main_database = MainDatabase()
        testG = testUserG(123, "Bob","Boberson")
        self.user_object = self.main_database.return_user_object(testG)
        self.assertEqual(self.main_database.users_database.iloc[0]["User Object"].first_name, "Bob")


    def test_add_strip(self): #Tests adding and accessing a strip in the database
        self.test_add_user()
        strip_obj_added = self.user_object.add_strip(1351221, 100, "Bob's Kitchen Lights")

        self.strip_obj_read = self.main_database.strips_database.loc[1351221]["Strip Object"]

        self.assertEqual(self.strip_obj_read.display_name, "Bob's Kitchen Lights")

    def test_remove_strip(self): #Tests adding and accessing a strip in the database
        self.test_add_strip()
        self.user_object.remove_strip(135122)

        self.assertEqual(len(self.main_database.strips_database.loc[1351221]),0)

    def test_set_SunPattern(self): #Tests adding and accessing a strip in the database
        self.test_add_strip()
        self.strip_obj_read.sections_list[0].set_pattern(SunPattern(44.49, 41.69, "US/Eastern", {'r':240,'g':100,'b':2}, {'r':240,'g':200,'b':100}, 123))
        self.strip_obj_read.update_light_statuses()

        self.assertEqual(self.strip_obj_read.sections_list[0].current_mode.get_description_string_small(),"Sun-based pattern")

    def test_set_TimePattern(self):  # Tests adding and accessing a strip in the database
        self.test_add_strip()
        self.strip_obj_read.sections_list[0].set_pattern(
            TimePattern({0:{'r': 240, 'g': 100, 'b': 2}, 1440:{'r': 240, 'g': 200, 'b': 100}}, 'fade',"US/Eastern", 'frshbsrfhsr'))
        self.strip_obj_read.update_light_statuses()

        self.assertEqual(self.strip_obj_read.sections_list[0].current_mode.get_description_string_small(),
                         "Time-based pattern")

    def test_add_section(self): #Tests adding and accessing a strip in the database
        self.test_add_strip()


        self.strip_obj_read.add_new_section_and_update(0,49)

        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_start_led, 0)#test the first section's start led
        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_end_led, 99)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_end_led, 49)

        self.strip_obj_read.add_new_section_and_update(0, 0)

        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_start_led,0)
        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_end_led, 99)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_end_led, 49)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_end_led, 0)

        self.strip_obj_read.add_new_section_and_update(100, 100)

        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_end_led, 99)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_end_led, 49)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_end_led, 0)

        self.strip_obj_read.add_new_section_and_update(-1, -1)

        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[0].initial_end_led, 99)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[1].initial_end_led, 49)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_start_led, 0)
        self.assertEqual((self.strip_obj_read.sections_list)[2].initial_end_led, 0)


    def test_get_light_status(self): #Tests getting the light status of a strip in the database
        self.test_add_section()


        self.assertEqual(self.strip_obj_read.return_light_status_as_json(), '{"range_start": 0, "range_end": 99, "range_status": {"mode": "so", "color": {"r": 255, "g": 255, "b": 229}}}')







if __name__ == '__main__':
    unittest.main()
