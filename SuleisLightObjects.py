import json, uuid
import pandas as pd
from abc import ABC, abstractmethod

class MainDatabase:
    def __init__(self):
        self.users_database = pd.DataFrame(columns=["User ID", "User Object"])
        self.strips_database = pd.DataFrame(columns=["Strip ID", "Strip Object"]) #use to make sure one strip isn't attached to multiple accounts

    def return_user_object(self,user): #returns the user's object if user is returning, or makes a new one and then returns it if it is a new user. If user is none (no logged in?), returns false
        if user != None:

            #user.profile.firstName
            #user.id
            try:
                user_obj = self.users_database.loc[user.id]["User Object"]
                return user_obj
            except:
                #This is a new user, so we'll add them to the database
                new_user = User(user.id,user.profile.firstName,user.profile.lastName, self)
                self.users_database = self.users_database.append(pd.Series({"User ID":new_user.user_id,"User Object":new_user},name=user.id))
                return new_user
        else:
            return False

    def check_and_add_strip(self, strip_id, leds_count, display_name): #if strip already exists, returns false, if strip is new, adds it to list and returns True
        try:
            strip_obj = self.strips_database.loc[strip_id]["Strip Object"]
            return False
        except:
            new_strip = Strip(strip_id,leds_count,display_name)
            self.strips_database = self.strips_database.append(pd.Series({"Strip ID": strip_id, "Strip Object": new_strip}, name=strip_id))
            return new_strip


class User:
    def __init__(self, user_id, first_name, last_name, main_database):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.light_strips = {}
        self.main_database = main_database

    def add_strip(self, strip_id, leds_count, display_name):

        if display_name in self.light_strips.keys():
            return "Error: light strip of same name already present in user account"
        else:
            strip_object = self.main_database.check_and_add_strip(strip_id,leds_count,display_name) #returns False if strip already registered, or the new strip object if not
            if strip_object:#strip is not on another account
                self.light_strips[display_name]=strip_object
                return True
            else:
                return "Error: this light strip is already registered to a user account"

    def remove_strip(self, strip_id): #IMPLEMENT THIS
        pass



class Strip:
    def __init__(self,strip_id,leds_count,display_name):
        self.leds_count = leds_count
        self.strip_id = strip_id
        self.display_name = display_name
        self.leds_and_sections = []
        self.default_section = Section(self,0, leds_count-1, "Section 1")
        #self.default_section.set_mode({"pattern":"solid_color","info":{"R":0,"G":193,"B":0}}) #Default mode is green (not white for now because sometimes the lights turn white if not connected properly)
        self.sections_list = [self.default_section]
        self.update_leds_and_sections()
        self.leds_and_statuses = None

    def get_section_by_id(self, section_id):
        for section in self.sections_list:
            if section.section_id == section_id:
                return section
        return False

    def get_pattern_by_id(self, pattern_id):
        for section in self.sections_list:
            if section.current_mode.pattern_id == pattern_id:
                print("section.current_mode.pattern_id")

                print(pattern_id)
                return section.current_mode
        return False

    def add_new_section_and_update(self,start_led,end_led):
        if start_led < 0:
            return "Error: section start led index is below 0"
        if end_led > self.leds_count-1:
            return "Error: section end led index is greater than that of the last led on the strip {self.leds_count-1}"
        self.sections_list.append(Section(self,start_led,end_led, f"Section {len(self.sections_list)+1}"))
        self.update_leds_and_sections()
        self.update_light_statuses()
        return True



    def update_leds_and_sections(self):
        #CALL THIS ANY TIME A NEW section IS ADDED (it's called automatically by add_new_section_and_update)
        #section priorities are in reverse-priority: if two overlap, the one added later prevails
        #sections have their led counts updated here
        leds_and_sections_new = [self.default_section for led in range(0,self.leds_count-1)]
        for led_num in range(0,self.leds_count-1):
            for section in self.sections_list:
                print(section.display_name)
                if (led_num <= section.initial_end_led) and (led_num >= section.initial_start_led):
                    leds_and_sections_new[led_num] = section
                    print(f"      {section.display_name}")
        #print(leds_and_sections_new)
        for section in self.sections_list:
            if section not in leds_and_sections_new:
                self.sections_list.remove(section)

        self.leds_and_sections = leds_and_sections_new


    def update_light_statuses(self):
        #for each uniqur section in this strip, call the update_light_status method
        #after we run this, we should be able to efficienntly assign each led
        #color/mode to the value of the associated strip's mode value SubSting.get_led_mode()
        new_modes_list = [None for led in range(0,self.leds_count-1)]

        for section in set(self.sections_list):
            section.update_light_status()

        for led_num in range(0,self.leds_count-1):
            new_modes_list[led_num] = self.leds_and_sections[led_num].get_light_status()

        self.leds_and_statuses = new_modes_list





    def return_sections_and_patterns_dict(self): #this returns a dict of each section's mode (not light status). We can use this for configuring the strip sections.


        ranges = []
        curr_range_start = 0
        curr_range_end = 0
        curr_range_pattern = self.leds_and_sections[0].current_mode
        for led_section in self.leds_and_sections:
            if curr_range_pattern == led_section.current_mode:
                curr_range_end += 1
            else:
                ranges.append({"range_start" : curr_range_start,"range_end" : curr_range_end, "range_pattern" : curr_range_pattern})
                curr_range_start = curr_range_end + 1
                curr_range_end = curr_range_start
                curr_range_pattern = led_section.current_mode
        ranges.append({"range_start": curr_range_start, "range_end": curr_range_end, "range_pattern": curr_range_pattern})
        #print(ranges)
        return ranges


    def return_light_status_as_json(self): #we should really just combine this with the sections thing so we only have to call get_light_status once per led
        self.update_light_statuses()  # could add something here to not call this if it was called in last X seconds
        ranges = []
        curr_range_start = 0
        curr_range_end = 0
        curr_range_status = self.leds_and_statuses[0]
        #range_num = 0
        for led_status in self.leds_and_statuses:
            if curr_range_status == led_status:
                curr_range_end += 1
            else:
                #ranges[range_num] = json.dumps(({"range_start" : curr_range_start,"range_end" : curr_range_end, "range_status" : curr_range_status}))
                ranges.append( json.dumps(({"range_start" : curr_range_start,"range_end" : curr_range_end, "range_status" : curr_range_status})))
                curr_range_start = curr_range_end + 1
                curr_range_end = curr_range_start
                curr_range_status = led_status
                #range_num +=1
        ranges.append(json.dumps(({"range_start": curr_range_start, "range_end": curr_range_end,
                                           "range_status": curr_range_status})))

        return "*".join(ranges)


class Section:
    def __init__(self, strip ,initial_start_led,initial_end_led, display_name):
        self.section_id = str(strip.strip_id) + str(display_name)
        self.current_leds_count = (initial_end_led - initial_end_led) + 1
        self.current_mode = None
        self.set_pattern(SolidPattern({'r':255,'g':255,'b':255}, str(uuid.uuid4())))
        self.current_light_status = None
        #self.update_light_status()
        self.initial_end_led = initial_end_led
        self.initial_start_led = initial_start_led
        self.display_name = display_name

    def set_pattern(self, new_mode):
        self.current_mode = new_mode


    def update_light_status(self):
        #code to automatically update the light status based on current time/weather
        #different from setting mode, which sets the pattern (a function relating time/weather and light status)
        self.current_light_status = self.current_mode.get_current_color_dict()



    def get_light_status(self):
        #returns light status.


        return self.current_light_status


"""
Here is a template that all of the Pattern classes will follow
class Pattern:
    def __int__(self, parameters):
    
    def get_current_color_dict:
    
"""


class Pattern(ABC):
    @abstractmethod
    def __int__(self, parameters):
        pass

    @abstractmethod
    def get_current_color_dict():
        pass

    @abstractmethod
    def get_description_string():
        pass


class SolidPattern:
    def __init__(self, color_dict, pattern_id):
        #Format of colorDict: {'r':255,'g':255,'b':255}
        if color_dict['g'] > 0:

            color_dict['g'] = min(int(1.1*color_dict['g']),255)
            #color_dict['r'] = int(0.95 * color_dict['r'])
            color_dict['b'] = int(0.90 * color_dict['b'])
        self.color_dict = color_dict

        self.pattern_id = pattern_id


    def get_current_color_dict(self):
        return self.color_dict

    def get_description_string(self):
        return f"Solid color: {self.color_dict}"

    def get_description_string_small(self):
        return f"Solid color pattern"


class TimePattern:
    def __init__(self, time_color_dicts, gradient_type, pattern_id):
        #Format of time_color_dicts: (0:{'r':255,'g':255,'b':255},180:{'r':255,'g':255,'b':255},600:{'r':255,'g':255,'b':255}), where the numbers 0, 180, and 600 represent minutes since the start of the day (week if we make that an option)
        #Format of gradient_type
        #time zone offset is nummber of hours to add to UTC to get the time zone (DST?)
        self.time_color_table = pd.DataFrame.from_dict(time_color_dicts)
        self.gradient_type = gradient_type
        self.time_zone_offset = time_zone_offset
        self.pattern_id = pattern_id

    def get_current_color_dict(self):
        period_minutes #= minutes since day begin
        if gradient_type == "fade":
            color_dict = self.time_color_table.append(pd.Series({'r':np.NaN,'g':np.NaN,'b':np.NaN},name=period_minutes)).interpolate(method='index').loc[period_minutes].to_dict.round().to_dict()


    def get_description_string(self):
        return f"Time-based pattern, current color: {self.get_current_color_dict()}"

    def get_description_string_small(self):
        return f"Time-based pattern"

