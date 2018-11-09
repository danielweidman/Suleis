from SuleisLightObjects import MainDatabase, User, Section, Strip, Pattern, SolidPattern, TimePattern
from flask import Flask, render_template, g, redirect, url_for
from flask_oidc import OpenIDConnect
from okta import UsersClient
import pickle
import uuid

#Initialize the components needed for the Okta accounts system


try: #Try to load the database from the saved pickle, make a new one if that fails
    main_database = pickle.load(open("user_database.p",'rb'))
except:
    main_database = MainDatabase()

def save_database(): #Save the database to a pickle file
    pickle.dump(main_database,open("user_database.p",'wb'))

@app.before_request
def before_request(): #Code for Okta login
    if oidc.user_loggedin:

        g.user = okta_client.get_user(oidc.user_getfield("sub"))
    else:
        g.user = None


@app.route("/")
def index(): #Serve homepage
    return render_template("index.html")


@app.route("/dashboard")
@oidc.require_login
def dashboard(): #Serve dashboard page
    user_object = main_database.return_user_object(g.user)
    save_database()
    return render_template("dashboard.html", user_object=user_object)


@app.route("/login")
@oidc.require_login
def login(): #Serve login page redirect
    return redirect(url_for(".dashboard"))


@app.route("/logout")
def logout(): #Process logout, redirect to homepage
    oidc.logout()
    return redirect(url_for(".index"))

@app.route("/add_strip/<strip_id>/<leds_count>/<display_name>")
@oidc.require_login
def add_strip(strip_id, leds_count, display_name): #Process adding a strip

    strip_id = strip_id.lower().strip(":").strip(" ")
    leds_count = int(leds_count)
    user_object = main_database.return_user_object(g.user)
    result = user_object.add_strip(strip_id, leds_count, display_name)
    print(result)

    if result == True:
        return render_template("dashboard.html", user_object=user_object)
    else:
        return result


@app.route("/get_strip_status/<strip_id>/")
def get_strip_status(strip_id): #Serve the strip status
    #print(main_database.strips_database)
    #strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
    try:
        strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
        return strip_obj.return_light_status_as_json()
    except Exception as e: #could do better exceptionn handling

        return f"{e}:Strip not found"


@app.route("/add_section/<strip_id>/<start_led>/<end_led>")
def add_section(strip_id,start_led,end_led): #Process adding a section
    #print(main_database.strips_database)
    #strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
    #strip_obj.add_new_section_and_update(int(start_led), int(end_led))
    #user_object = main_database.return_user_object(g.user)
    #return render_template("dashboard.html", user_object=user_object)

    try:
        strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
        result = strip_obj.add_new_section_and_update(int(start_led), int(end_led))
        if result == True:
            user_object = main_database.return_user_object(g.user)
            return render_template("dashboard.html", user_object=user_object)
        else:
            return result
    except Exception as e: #could do better exceptionn handling

        return f"{e}:Strip not found or other error"


@app.route("/set_section_solid_pattern/<strip_id>/<section_id>/<R>,<G>,<B>") #Only for SolidPatterns at the moment
@oidc.require_login
def set_section_solid_pattern(strip_id, section_id,R,G,B): #Process setting a section pattern
    #print(main_database.strips_database)
    strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
    section_obj = strip_obj.get_section_by_id(section_id)
    if section_obj != False:
        section_obj.set_pattern(SolidPattern(int(R),int(G),int(B)),str(uuid.uuid4()))
        return redirect("/dashboard")

    else:
        return "Error finding that section"


@app.route("/set_pattern_solid_color/<strip_id>/<pattern_id>/<R>,<G>,<B>") #JUST FOR TESting, need to accommodate different info block parameters
@oidc.require_login
def set_pattern_solid_color(strip_id, pattern_id,R,G,B): #Process moodifying a SolidPattern's color
    #print(main_database.strips_database)
    strip_obj = main_database.strips_database.loc[strip_id]["Strip Object"]
    pattern_obj = strip_obj.get_pattern_by_id(pattern_id)
    if pattern_obj != False:
        pattern_obj.color_dict = {'r':R,'g':G,"b":B}
        return redirect("/dashboard")

    else:
        return "Error finding that section"

@app.route("/create_sunrise_sunet_pattern/<strip_id>/<section_id>") #JUST FOR TESting, need to accommodate different info block parameters
@oidc.require_login
def create_sunrise_sunset_page(strip_id, section_id):
    lat = reader.get(request.remote_addr)['location']['latitude']
    lon = reader.get(request.remote_addr)['location']['longitude']

    return "something"


