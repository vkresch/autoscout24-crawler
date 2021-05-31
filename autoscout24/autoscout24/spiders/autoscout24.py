# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import Request
from scrapy.loader.processors import Join, MapCompose, Compose, TakeFirst, Identity

from autoscout24.items import CarsItem
from autoscout24.properties.properties import Make, SortCriteria, SortDirection, VehicleCondition, Gear
from autoscout24.properties.location import Country, City, LocationRadius
from autoscout24.properties.equipment import Equipment
from autoscout24.properties.price import PriceFrom, PriceTo
from autoscout24.properties.mileage import MileageTo

from urllib.parse import urljoin
from w3lib.html import remove_tags, replace_escape_chars
import datetime
import socket
import uuid


class Autoscout24Spider(scrapy.Spider):
    MAX_PAGES = 20
    name = 'autoscout24'
    allowed_domains = ['web', 'autoscout24.com']
    start_urls = ['https://www.autoscout24.com/lst?&sort=age&desc=1&ustate=N%2CU&size=20&cy=D&atype=C&page=1']

    def parse(self, response):
        page_count = 20
        # Get the next index URLs and yield Requests
        for make in Make:
            for sortcrit in SortCriteria:
                for desc in SortDirection:
                    for idx in range(1, page_count+1):                    
                        yield Request(
                            'https://www.autoscout24.com/lst'
                            + make.value
                            + '?&sort='
                            + sortcrit.value
                            + '&'
                            + desc.value
                            + '&offer='
                            + VehicleCondition.USED.value
                            + '&eq='
                            + Equipment.ALL.value
                            + '&gear='
                            + Gear.AUTOMATIC.value
                            + '&ustate=N%2CU&size=20&cy='
                            + Country.GERMANY.value
                            + '&zip='
                            + City.MUNICH.value
                            + '&zipr='
                            + LocationRadius.DIST_100km.value
                            + '&priceto='
                            + PriceTo.TO_10000.value
                            + '&kmto='
                            + MileageTo.TO_100000.value
                            + '&pricefrom='
                            + PriceFrom.FROM_3000.value
                            + '&atype=C&page='
                            + str(idx)
                        )

        # Get item URLs and yield Requests
        item_selector = response.xpath('//*[@class="cldt-summary-titles"]/a/@href')
        for url in item_selector.extract():
            yield Request(urljoin(response.url, url), callback=self.parse_item)

    def parse_item(self, response):
        """ This function parses a car page.
        @url https://www.autoscout24.com/offers/ferrari-monza-sp2-ready-now-export-worldwide-gasoline-red-662f3a46-7168-46e5-b284-6636e5276303?cldtidx=1&cldtsrc=listPage
        @returns items 1
        @scrapes make model version registration price_euro driven_km power_kW
        @scrapes url project spider server date
        """

        self.log("Visited %s" % response.url)
        l = ItemLoader(item=CarsItem(), response=response)
        
        l.add_xpath('price_euro', '//*[@class="cldt-stage-headline"]/div[1]/h2/text()', TakeFirst(), MapCompose(lambda i: i.replace(',',''), float, str), re='[,.0-9]+')
        l.add_xpath('driven_km', '//*[@class="cldt-stage-basic-data"]/div[1]/span/text()', TakeFirst(), MapCompose(lambda i: i.replace(',',''), float, str), re='[,.0-9]+')
        l.add_xpath('power_kW', '//*[@class="cldt-stage-basic-data"]/div[3]/span/text()', TakeFirst(), MapCompose(lambda i: i.replace(',',''), float, str), re='[,.0-9]+')

        # Properties
        l.add_xpath('make', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Make"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('model', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Model"]/following::dd[1]/a/text()', MapCompose(replace_escape_chars))
        l.add_xpath('version', '//*[@class="cldt-detail-version sc-ellipsis"]/text()', TakeFirst(), MapCompose(replace_escape_chars))
        l.add_xpath('registration', '//*[@id="basicDataFirstRegistrationValue"]/text()', TakeFirst(), MapCompose(replace_escape_chars))
        l.add_xpath('offer_number', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Offer Number"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('body_color', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Body Color"]/following::dd[1]/a/text()', MapCompose(replace_escape_chars))

        l.add_xpath('paint_type', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Paint Type"]/following::dd[1]/text()', MapCompose(replace_escape_chars), TakeFirst())
        l.add_xpath('body_color_original', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Body Color Original"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('upholstery', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Upholstery"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('body', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Body"]/following::dd[1]/a/text()', MapCompose(replace_escape_chars))
        l.add_xpath('number_doors', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Nr. of Doors"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('number_seats', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Nr. of Seats"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('model_code', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Model Code"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('country_version', '//*[@class="sc-font-bold"][text()="Properties"]/following::dl/dt[text()="Country version"]/following::dd[1]/text()', MapCompose(replace_escape_chars))

        # State
        l.add_xpath('usage_type', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Type"]/following::dd[1]/a/text()')
        l.add_xpath('available', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Available"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('owner_count', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Previous Owners"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('inspection_new', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Inspection new"]/following::dd[1]/text()', MapCompose(replace_escape_chars), TakeFirst())
        l.add_xpath('last_service', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Last Service Date"]/following::dd[1]/text()', MapCompose(replace_escape_chars), TakeFirst())
        l.add_xpath('warranty', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Warranty"]/following::dd[1]/text()', MapCompose(lambda i: 'Yes'), TakeFirst())
        l.add_xpath('full_service', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Full Service"]/following::dd[1]//@type', MapCompose(lambda i: 'Yes'), TakeFirst())
        l.add_xpath('non_smoking', '//*[@class="sc-font-bold"][text()="State"]/following::dl/dt[text()="Non-smoking Vehicle"]/following::dd[1]/text()', MapCompose(lambda i: 'Yes'), TakeFirst())

        # Drive
        l.add_xpath('gearing_type', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Gearing Type"]/following::dd[1]/a/text()', MapCompose(replace_escape_chars))
        l.add_xpath('gears', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Gears"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('displacement_cc', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Displacement"]/following::dd[1]/text()', MapCompose(lambda i: i.replace(',',''), float, str), re='[,.0-9]+')
        l.add_xpath('weight_kg', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Weight"]/following::dd[1]/text()', MapCompose(lambda i: i.replace(',',''), float, str), re='[,.0-9]+')
        l.add_xpath('drive_chain_WD', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Drive chain"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('cylinders', '//*[@class="sc-font-bold"][text()="Drive"]/following::dl/dt[text()="Cylinders"]/following::dd[1]/text()', MapCompose(replace_escape_chars), TakeFirst())

        # Environment
        l.add_xpath('fuel', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Fuel"]/following::dd[1]/a/text()', MapCompose(replace_escape_chars))
        l.add_xpath('consumption_comb', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Consumption"]/following::dd[1]/div[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('consumption_city', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Consumption"]/following::dd[1]/div[2]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('consumption_country', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Consumption"]/following::dd[1]/div[3]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('co2_emission', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="CO2 Emission"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('emission_class', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Emission Class"]/following::dd[1]/text()', MapCompose(replace_escape_chars))
        l.add_xpath('emission_label', '//*[@class="sc-font-bold sc-grid-col-s-12"][text()="Environment"]/following::div/div/dl/dt[text()="Emission Label"]/following::dd[1]/text()', MapCompose(replace_escape_chars))

        # Equipment
        l.add_xpath('air_conditioning', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Air conditioning"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('armrest', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Armrest"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('automatic_climate_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Automatic climate control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('auxiliary_heating', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Auxiliary heating"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('cruise_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Cruise control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('electrically_adjustable_seats', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Electrically adjustable seats"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('electrical_sidemirrors', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Electrical side mirrors"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('electric_tailgate', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Electric tailgate"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('heads_up_display', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Heads-up display"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('heated_steering_wheel', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Heated steering wheel"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('hill_holder', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Hill Holder"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('keyless_central_door_lock', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Keyless central door lock"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('leather_steering_wheel', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Leather steering wheel"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('light_sensor', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Light sensor"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('lumbar_support', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Lumbar support"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('massage_seats', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Massage seats"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('multi_function_steering_wheel', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Multi-function steering wheel"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('navigation_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Navigation system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('panorama_roof', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Panorama roof"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('park_distance_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Park Distance Control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('parking_assist_system_camera', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Parking assist system camera"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('parking_assist_system_self_steering', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Parking assist system self-steering"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('parking_assist_system_sensors_front', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Parking assist system sensors front"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('parking_assist_system_sensors_rear', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Parking assist system sensors rear"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('power_windows', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Power windows"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('rain_sensor', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Rain sensor"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('seat_heating', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Seat heating"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('seat_ventilation', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Seat ventilation"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('split_rear_seats', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Split rear seats"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('start_stop_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Start-stop system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sunroof', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sunroof"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('tinted_windows', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Tinted windows"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('wind_deflector', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Wind deflector"]', MapCompose(lambda i: 'Yes'))
        # Winshield
        
        l.add_xpath('bluetooth', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Bluetooth"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('cd_player', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="CD player"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('digital_radio', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Digital radio"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('hands_free_equipment', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Hands-free equipment"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('mp3', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="MP3"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('onboard_computer', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="On-board computer"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('radio', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Radio"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sound_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sound system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('television', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Television"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('usb', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="USB"]', MapCompose(lambda i: 'Yes'))
        
        l.add_xpath('wd4', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="4WD"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('alloy_wheels', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Alloy wheels"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('cab_or_rented', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Cab or rented Car"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('catalytic_converter', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Catalytic Converter"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('handicapped_enabled', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Handicapped enabled"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('right_hand_drive', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Right hand drive"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('roof_rack', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Roof rack"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('shift_paddles', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Shift paddles"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('ski_bag', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Ski bag"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sliding_door', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sliding door"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sport_package', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sport package"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sport_seats', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sport seats"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('sport_suspension', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Sport suspension"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('touch_screen', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Touch screen"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('trailer_hitch', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Trailer hitch"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('tuned_car', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Tuned car"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('voice_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Voice Control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('winter_tyres', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Winter tyres"]', MapCompose(lambda i: 'Yes'))
        
        l.add_xpath('abs_car', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="ABS"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('adaptive_cruise_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Adaptive Cruise Control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('adaptive_headlights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Adaptive headlights"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('alarm_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Alarm system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('blind_spot_monitor', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Blind spot monitor"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('central_door_lock', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Central door lock"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('daytime_running_lights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Daytime running lights"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('driver_drowsiness_detection', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Driver drowsiness detection"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('driver_side_airbag', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Driver-side airbag"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('electronic_stability_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Electronic stability control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('emergency_brake_assistant', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Emergency brake assistant"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('emergency_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Emergency system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('fog_lights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Fog lights"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('head_airbag', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Head airbag"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('immobilizer', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Immobilizer"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('isofix', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Isofix"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('lane_departure_warning_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Lane departure warning system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('led_daytime_running_lights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="LED Daytime Running Lights"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('led_headlights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="LED Headlights"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('night_view_assist', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Night view assist"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('power_steering', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Power steering"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('rear_airbag', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Rear airbag"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('side_airbag', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Side airbag"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('tire_pressure_monitoring_system', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Tire pressure monitoring system"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('traction_control', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Traction control"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('traffic_sign_recognition', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Traffic sign recognition"]', MapCompose(lambda i: 'Yes'))
        l.add_xpath('xenon_headlights', '//*[@class="cldt-equipment-block sc-grid-col-3 sc-grid-col-m-4 sc-grid-col-s-12 sc-pull-left"]/span[text()="Xenon headlights"]', MapCompose(lambda i: 'Yes'))
        
        l.add_value('url', response.url)
        l.add_value('sha', uuid.uuid4().hex)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        return l.load_item()