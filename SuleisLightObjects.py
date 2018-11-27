import json, uuid, astral
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import datetime
import pytz, copy

DYNAMIC_PATTERN_NAMES = {'cc': 'Color cycle', 'rb': 'Rainbow', 'cs': 'Strobe (color)', 'ws': 'Strobe (white)',
                         'pp': 'Ping-pong', 'sp': 'Ping-pong (with acceleration)'}


class MainDatabase: #Class that represents main database of users, strips, sections, and active patterns
    def __init__(self):
        self.users_database = pd.DataFrame(columns=["User ID", "User Object"]) #DataFrame of users for fast user locating
        self.strips_database = pd.DataFrame(columns=["Strip ID", "Strip Object"]) #use to make sure one strip isn't attached to multiple accounts, and fast strip object locating
    def return_user_object(self,user): #returns the user's object if user is returning, or makes a new one and then returns it if it is a new user. If user is none (no logged in?), returns false
        if user != None:

            try:
                #Existing user
                user_obj = self.users_database.loc[user.id]["User Object"]
                return user_obj
            except:
                #This is a new user, so we'll add them to the database
                new_user = User(user.id,user.profile.firstName,user.profile.lastName, self)
                self.users_database = self.users_database.append(pd.Series({"User ID":new_user.user_id,"User Object":new_user},name=user.id))
                return new_user
        else:
            return False

    def check_and_add_strip(self, strip_id, leds_count, display_name): #if strip already exists, returns false, if strip is new, adds it to list and return the strip object
        try:
            strip_obj = self.strips_database.loc[strip_id]["Strip Object"] #Returns error if strip not already in database

            return False #Returns error if strip not already in database

        except:
            #Add the strip
            new_strip = Strip(strip_id,leds_count,display_name)
            self.strips_database = self.strips_database.append(pd.Series({"Strip ID": strip_id, "Strip Object": new_strip}, name=strip_id))
            return new_strip


class User: #Class to represent a user. Can aggregate multiple strips
    def __init__(self, user_id, first_name, last_name, main_database): #user_id from the OIDC/Okta service, see app.py
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.light_strips = {}
        self.main_database = main_database

    def add_strip(self, strip_id, leds_count, display_name): #add new strip to user with given parameters

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



class Strip: #Class representing a Strip. Can aggregate multiple sections.
    def __init__(self,strip_id,leds_count,display_name):
        self.leds_count = leds_count
        self.strip_id = strip_id
        self.display_name = display_name
        self.leds_and_sections = [] #List that stores a pointer to the relevant section for each LED (could makke this more memory efficient on average by storing only ranges and sections)
        self.default_section = Section(self,0, leds_count-1, "Section 1") #Make aa default section for this strip
        self.sections_list = [self.default_section] #List of all active sections in this strip. Inactive sections (those covered fully by new section(s)) will be removed.
        self.update_leds_and_sections()
        self.leds_and_statuses = None

    def get_section_by_id(self, section_id): #Returns the section belonging to this Strip with the given id (or False)
        for section in self.sections_list:
            if section.section_id == section_id:
                return section
        return False

    def get_pattern_by_id(self, pattern_id):#Returns the pattern belonging to this Strip with the given id (or False)
        for section in self.sections_list:
            if section.current_mode.pattern_id == pattern_id:

                print("section.current_mode.pattern_id")

                print(pattern_id)
                return section.current_mode
        return False

    def add_new_section_and_update(self,start_led,end_led): #Add new section to the strip (and test that the range is valid
        if start_led < 0:
            return "Error: section start led index is below 0"
        if end_led > self.leds_count-1:
            return f"Error: section end led index is greater than that of the last led on the strip {self.leds_count}" #user might see this as 99?

        self.sections_list.append(Section(self,start_led,end_led, f"Section {len(self.sections_list)+1}"))
        self.update_leds_and_sections()
        self.update_light_statuses()
        return True



    def update_leds_and_sections(self):
        #CALL THIS ANY TIME A NEW Section IS ADDED (it's called automatically by add_new_section_and_update)
        #Section priorities are in reverse-priority: if two overlap, the one added later prevails
        leds_and_sections_new = [self.default_section for led in range(0,self.leds_count)]
        for led_num in range(0,self.leds_count):
            for section in self.sections_list:
                #print(section.display_name)
                if (led_num <= section.initial_end_led) and (led_num >= section.initial_start_led):
                    leds_and_sections_new[led_num] = section
                    #print(f"      {section.display_name}")
        #print(leds_and_sections_new)
        for section in self.sections_list:
            if section not in leds_and_sections_new:
                self.sections_list.remove(section)

        sections_found = []
        last_section_found = None
        for led_num in range(0, self.leds_count): #check if there are any sections that got split by the new section. If so, we should make those act independently, but share the same initial pattern settings
            if leds_and_sections_new[led_num] == last_section_found:
                leds_and_sections_new[led_num] = last_section_found

            elif (leds_and_sections_new[led_num] in sections_found) and (not leds_and_sections_new[led_num] == last_section_found):
                #We have just hit the first LED in a range that has the same section object as an earlier one
                cut_in_half_section = leds_and_sections_new[led_num] #this is the one we'll have to copy and replace
                new_section = copy.deepcopy(cut_in_half_section)
                new_section.display_name = f"{new_section.display_name}c"
                new_section.section_id = f"{new_section.section_id}c"
                new_section.current_mode.pattern_id = str(uuid.uuid4())
                last_section_found = new_section
                leds_and_sections_new[led_num] = new_section
                for led_num2 in range(led_num+1,self.leds_count):
                    if leds_and_sections_new[led_num2] == cut_in_half_section:
                        leds_and_sections_new[led_num2] = new_section
                        print("propagated")
                    else:
                        break
                self.sections_list.append(new_section)
                print("made new section")

            elif leds_and_sections_new[led_num] not in sections_found:
                sections_found.append(leds_and_sections_new[led_num])
                last_section_found = leds_and_sections_new[led_num]

        self.leds_and_sections = leds_and_sections_new


    def update_light_statuses(self):
        #For each unique section in this strip, call the update_light_status method
        #After we run this, we should be able to efficienntly assign each pixel status in the Strip
        new_modes_list = [None for led in range(0,self.leds_count)]

        for section in set(self.sections_list):
            section.update_light_status()

        for led_num in range(0,self.leds_count):
            new_modes_list[led_num] = self.leds_and_sections[led_num].get_light_status()

        self.leds_and_statuses = new_modes_list





    def return_sections_and_patterns_dict(self): #Returns a dict of each section's Pattern (not light status). We can use this for configuring the strip sections.

        ranges = []
        curr_range_start = 0
        curr_range_end = -1
        curr_range_pattern = self.leds_and_sections[0].current_mode
        curr_range_section = self.leds_and_sections[0]
        for led_section in self.leds_and_sections:
            if curr_range_pattern == led_section.current_mode:
                curr_range_end += 1
            else:
                ranges.append({"range_start" : curr_range_start,"range_end" : curr_range_end, "range_pattern" : curr_range_pattern, "range_section" : curr_range_section})
                curr_range_start = curr_range_end + 1
                curr_range_end = curr_range_start
                curr_range_pattern = led_section.current_mode
                curr_range_section = led_section
        ranges.append({"range_start": curr_range_start, "range_end": curr_range_end, "range_pattern": curr_range_pattern, "range_section" : curr_range_section})
        #print(ranges)
        return ranges


    def return_light_status_as_json(self): #Returns an * delimited list of JSON strings representing each Section (and associated light status) in the list.
        #We chould really just combine this with the sections thing so we only have to call get_light_status once per led
        self.update_light_statuses()  #Could add something here to not call this if it was called in last X seconds (NO: actually put that stuff in the pattern object, in case pattern is changed)
        ranges = []
        curr_range_start = 0
        curr_range_end = -1
        curr_range_status = self.leds_and_statuses[0]
        #range_num = 0
        for led_status in self.leds_and_statuses:
            if curr_range_status == led_status:
                curr_range_end += 1
            else:
                ranges.append( json.dumps(({"range_start" : curr_range_start,"range_end" : curr_range_end, "range_status" : curr_range_status})))
                curr_range_start = curr_range_end + 1
                curr_range_end = curr_range_start
                curr_range_status = led_status
                #range_num +=1
        ranges.append(json.dumps(({"range_start": curr_range_start, "range_end": curr_range_end,
                                           "range_status": curr_range_status})))
        #print("*".join(ranges))
        return "*".join(ranges)


class Section: #Class to represent a Section of lights. Has a Pattern.
    def __init__(self, strip ,initial_start_led,initial_end_led, display_name):
        self.section_id = str(strip.strip_id) + str(display_name)
        self.current_leds_count = (initial_end_led - initial_end_led) + 1
        self.current_mode = None
        self.set_pattern(SolidPattern({'r':255,'g':255,'b':255}, str(uuid.uuid4()))) #Set the default pattern to a solid 'warm' light color
        self.current_light_status = None
        #self.update_light_status()
        self.initial_end_led = initial_end_led
        self.initial_start_led = initial_start_led
        self.display_name = display_name

    def set_pattern(self, new_mode):
        self.current_mode = new_mode


    def update_light_status(self): #Calls the appropriate update function for the associated pattern, and stores the current light status
        #different from setting mode, which sets the pattern (a function relating time/weather and light status)
        self.current_light_status = self.current_mode.get_current_status_dict()



    def get_light_status(self):#Returns light status.

        return self.current_light_status




class Pattern(ABC):
    @abstractmethod
    def __int__(self, parameters):
        pass

    @abstractmethod
    def get_current_status_dict():
        pass

    @abstractmethod
    def get_description_string():
        pass

    def get_description_string_small(self):
        pass


class SolidPattern:
    def __init__(self, color_dict, pattern_id):
        #Format of colorDict: {'r':255,'g':255,'b':255}
        if color_dict['b'] > 0:

            color_dict['r'] = min(int(1.05*color_dict['g']),255)
            #color_dict['g'] = int(0.95 * color_dict['r'])
            color_dict['b'] = int(0.95 * color_dict['b'])
        self.color_dict = color_dict

        self.pattern_id = pattern_id


    def get_current_status_dict(self): #Returns dict describing the currrent color of the pattern


        return {'mode':'so','color':self.color_dict}

    def get_description_string(self): #Gives string describing pattern type and current status
        return f"Solid color: {self.color_dict}"

    def get_description_string_small(self): #Gives string descring only pattern type
        return f"Solid color pattern"


class TimePattern:
    def __init__(self, time_color_dicts, gradient_type, time_zone, pattern_id):
        #Format of time_color_dicts: (0:{'r':255,'g':255,'b':255},180:{'r':255,'g':255,'b':255},600:{'r':255,'g':255,'b':255}), where the numbers 0, 180, and 600 represent minutes since the start of the day
        #Format of gradient_type

        self.time_color_table = pd.DataFrame.from_dict(time_color_dicts, orient='index')
        self.gradient_type = gradient_type
        self.time_zone = time_zone
        self.pattern_id = pattern_id


        self.color_dict = None

    def get_current_status_dict(self):
        now = datetime.datetime.now(pytz.timezone(self.time_zone))

        minutes_since_midnight = round((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()/60)
        if self.gradient_type == "fade":
            self.color_dict = self.time_color_table.append(pd.Series({'r':np.NaN,'g':np.NaN,'b':np.NaN},name=minutes_since_midnight)).interpolate(method='index').round().loc[minutes_since_midnight].to_dict()

        return {'mode':'solid','color':self.color_dict}

    def get_description_string(self):
        return f"Time-based pattern, current color: {self.color_dict}"

    def get_description_string_small(self):
        return f"Time-based pattern"


class DynamicPattern:
    def __init__(self, pattern_code, pattern_id):
        self.pattern_id = pattern_id;
        self.pattern_name = DYNAMIC_PATTERN_NAMES[pattern_code]
        self.pattern_code = pattern_code

    def get_current_status_dict(self):
        return {'mode':self.pattern_code, 'color':{'r':0,'g':0,'b':0}}

    def get_description_string(self):
        return f"{self.pattern_name} pattern"

    def get_description_string_small(self):
        return f"{self.pattern_name} pattern"


class SunPattern:
    def __init__(self, lat, long, time_zone, sun_down_color_dict, sun_up_color_dict, pattern_id):
        self.pattern_id = pattern_id
        self.sun_down_color_dict = sun_down_color_dict
        self.sun_up_color_dict = sun_up_color_dict
        self.lat = lat
        self.long = long
        self.time_zone = time_zone

    def get_current_status_dict(self):
        now = datetime.datetime.now(pytz.timezone(self.time_zone))

        minutes_since_midnight_now = round((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()/60)

        loc = astral.Location(('place','place',self.lat,self.long,self.time_zone))
        print(self.lat)
        print(self.long)
        minutes_since_midnight_dawn = round((loc.dawn() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()/60)

        minutes_since_midnight_sunrise = round((loc.sunrise() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60)
        minutes_since_midnight_sunset = round(
            (loc.sunset() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60)
        minutes_since_midnight_dusk= round(
            (loc.dusk() - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60)


        self.time_color_table =  pd.DataFrame.from_dict({0:self.sun_down_color_dict, minutes_since_midnight_dawn:self.sun_down_color_dict,minutes_since_midnight_sunrise:self.sun_up_color_dict,minutes_since_midnight_sunset:self.sun_up_color_dict,minutes_since_midnight_dusk:self.sun_down_color_dict}, orient='index')

        #3print(self.time_color_table.append(pd.Series({'r':np.NaN,'g':np.NaN,'b':np.NaN},name=minutes_since_midnight_now)).interpolate(method='index'))
        current_color = self.time_color_table.append(pd.Series({'r':np.NaN,'g':np.NaN,'b':np.NaN},name=minutes_since_midnight_now)).interpolate(method='index').round().loc[minutes_since_midnight_now].to_dict()
        return {'mode':'solid','color':current_color}


    def get_description_string(self):
        return "Sun-based pattern"

    def get_description_string_small(self):
        return "Sun-based pattern"






