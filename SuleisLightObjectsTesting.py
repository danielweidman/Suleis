import unittest

from SuleisLightObjects import MainDatabase, User, Section, Strip, Pattern, SolidPattern, TimePattern


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

    def test_get_light_status(self): #Tests getting the light status of a strip in the database
        self.test_add_strip()


        self.assertEqual(self.strip_obj_read.return_light_status_as_json(), '{"range_start": 0, "range_end": 99, "range_status": {"r": 255, "g": 255, "b": 229}}')







if __name__ == '__main__':
    unittest.main()
