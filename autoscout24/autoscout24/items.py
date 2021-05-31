# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from scrapy.loader.processors import Join, MapCompose, TakeFirst


class CarsItem(Item):
    # Primary fields
    price_euro = Field()
    driven_km = Field()
    power_kW = Field()

    # Properties
    make = Field()
    model = Field()
    version = Field()
    offer_number = Field()
    registration = Field()
    body_color = Field()
    paint_type = Field()
    body_color_original = Field()
    upholstery = Field()
    body = Field()
    number_doors = Field()
    number_seats = Field()
    model_code = Field()
    country_version = Field()

    # State
    usage_type = Field()
    available = Field()
    owner_count = Field()
    inspection_new = Field()
    last_service = Field()
    warranty = Field()
    full_service = Field()
    non_smoking = Field()

    # Drive
    gearing_type = Field()
    gears = Field()
    displacement_cc = Field()
    drive_chain_WD = Field()
    weight_kg = Field()
    cylinders = Field()

    # Environment
    fuel = Field()
    consumption_comb = Field()
    consumption_city = Field()
    consumption_country = Field()
    co2_emission = Field()
    emission_class = Field()
    emission_label = Field()

    # Equipment
    # Comfort
    air_conditioning = Field() 
    armrest = Field() 
    automatic_climate_control = Field() 
    auxiliary_heating = Field() 
    cruise_control = Field() 
    electrically_adjustable_seats = Field() 
    electrical_sidemirrors = Field() 
    electric_tailgate = Field() 
    heads_up_display = Field() 
    heated_steering_wheel = Field()
    hill_holder = Field() 
    keyless_central_door_lock = Field() 
    leather_steering_wheel = Field() 
    light_sensor = Field() 
    lumbar_support = Field() 
    massage_seats = Field()
    multi_function_steering_wheel = Field()
    navigation_system = Field() 
    panorama_roof = Field() 
    park_distance_control = Field() 
    parking_assist_system_camera = Field() 
    parking_assist_system_self_steering = Field()
    parking_assist_system_sensors_front = Field() 
    parking_assist_system_sensors_rear = Field() 
    power_windows = Field() 
    rain_sensor = Field() 
    seat_heating = Field() 
    seat_ventilation = Field() 
    split_rear_seats = Field()
    start_stop_system = Field()
    sunroof = Field()
    tinted_windows = Field()
    wind_deflector = Field()

    # Entertainment
    bluetooth = Field() 
    cd_player = Field()
    digital_radio = Field()
    hands_free_equipment = Field() 
    mp3 = Field()
    onboard_computer = Field()
    radio = Field()
    sound_system = Field()
    television = Field()
    usb = Field()

    # Extras
    wd4 = Field() 
    alloy_wheels = Field() 
    cab_or_rented = Field()
    catalytic_converter = Field()
    handicapped_enabled = Field()
    right_hand_drive = Field()
    roof_rack = Field() 
    shift_paddles = Field()
    ski_bag = Field()
    sliding_door = Field()
    sport_package = Field() 
    sport_seats = Field() 
    sport_suspension = Field() 
    touch_screen = Field()
    trailer_hitch = Field() 
    tuned_car = Field()
    voice_control = Field()
    winter_tyres = Field()

    # Safety
    abs_car = Field() 
    adaptive_cruise_control = Field() 
    adaptive_headlights = Field() 
    alarm_system = Field() 
    blind_spot_monitor = Field() 
    central_door_lock = Field() 
    daytime_running_lights = Field() 
    driver_drowsiness_detection = Field() 
    driver_side_airbag = Field() 
    electronic_stability_control = Field() 
    emergency_brake_assistant = Field()
    emergency_system = Field() 
    fog_lights = Field() 
    head_airbag = Field()
    immobilizer = Field()
    isofix = Field() 
    lane_departure_warning_system = Field() 
    led_daytime_running_lights = Field() 
    led_headlights = Field() 
    night_view_assist = Field()
    power_steering = Field() 
    rear_airbag = Field()
    side_airbag = Field() 
    tire_pressure_monitoring_system = Field() 
    traction_control = Field() 
    traffic_sign_recognition = Field()
    xenon_headlights = Field()

    # Housekeeping fields
    url = Field()
    sha = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()

