import os
import requests
import json
from time import sleep  
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse, parse_qs
import logging

# logging.basicConfig(level=logging.DEBUG)

def setup_driver(is_headless=True):
    options = Options()
    options.headless = is_headless

    geckodriver_path = "%s/drivers/geckodriver" % (os.getcwd())

    return webdriver.Firefox(options=options)

def _get_cookies(driver):
    cookies = driver.get_cookies()
    result = {}
    for cookie in cookies:
        result[cookie['name']] = cookie['value']

    return result

def _find_element_by_id(driver, _id):
    return driver.find_element_by_id(_id)

def _find_element_by_name(driver, _name):
    return driver.find_element_by_name(_name)

def click_id(driver, _id):
    click_el(driver, _find_element_by_id(driver, _id))

def click_el(driver, el):
    el.click()

def send_text_by_el(el, text):
    el.clear()
    el.send_keys(text)

def send_text_by_id(driver, _id, text):
    textbox = _find_element_by_id(driver, _id)
    send_text_by_el(textbox, text)

def launch_tax_assessor(driver):
    driver.get('http://blue.kingcounty.com/Assessor/eRealProperty/default.aspx')

    input_box_id = 'kingcounty_gov_cphContent_checkbox_acknowledge'
    click_id(driver, input_box_id)

def get_parcel_num_by_url(driver):

    while True:
        try:
            url = driver.current_url
            query = urlparse(url).query
            parcel_num = parse_qs(query)['ParcelNbr'][0]
            break
        except:
            pass
    
    return parcel_num

def goto_property_detail(driver):
    click_id(driver, 'kingcounty_gov_cphContent_LinkButtonDetail')

def get_parcel_id(driver):
    parcel_data_id = 'kingcounty_gov_cphContent_DetailsViewParcel'

    parcel_el = _find_element_by_id(driver, parcel_data_id)

    els = []
    while not els:
        els = parcel_el.find_elements_by_class_name("GridViewRowStyle")

    result = ''
    for el in els:
        if 'Parcel' in el.text:
            tmp = el.text.split(" ")[1].split("-")
            result = "%s%s" % (tmp[0], tmp[1])

    return result

def get_land_data(driver):
    land_data_id = 'kingcounty_gov_cphContent_DetailsViewLand'

    el = _find_element_by_id(driver, land_data_id)

    return el.text

def get_building_data(driver):
    building_data_id = 'kingcounty_gov_cphContent_DetailsViewResBldg'

    el = _find_element_by_id(driver, building_data_id)

    return el.text

def get_tax_historical_data(driver):
    tax_historical_data_id = 'kingcounty_gov_cphContent_GridViewTaxRoll'

    el = _find_element_by_id(driver, tax_historical_data_id)

    return el.text




def launch_property_tax_site(driver):
    driver.get('https://payment.kingcounty.gov/Home/Index?app=PropertyTaxes')

def search_tax_account_num(driver, parcel_num):
    input_field_name = 'searchParcel'
    print(driver.title)

    try:
        search_field = _find_element_by_name(driver, input_field_name)
        send_text_by_el(search_field, parcel_num)

        els = []
        while not els:
            els = driver.find_elements_by_class_name("input-group-btn")

        search_button_el = els[0]

        button_el = search_button_el.find_elements_by_class_name('btn-primary')[0]

        actions = ActionChains(driver)
        actions.move_to_element(search_button_el)

        actions.click(button_el)
        actions.perform()

    except Exception as e:
        raise e

def search_by_address(driver, address, city, zipcode):
    address_textbox_id = 'kingcounty_gov_cphContent_txtAddress'
    city_textbox_id = 'kingcounty_gov_cphContent_txtCity'
    zipcode_textbox_id = 'kingcounty_gov_cphContent_txtZip'
    search_button_id = 'kingcounty_gov_cphContent_btn_SearchAddress'


    el = None
    while not el:
        try:
            el = driver.find_element_by_id(address_textbox_id)
        except:
            pass

    send_text_by_id(driver, address_textbox_id, address)
    send_text_by_id(driver, city_textbox_id, city)
    send_text_by_id(driver, zipcode_textbox_id, zipcode)

    click_id(driver, search_button_id)

def get_tax_account_num(driver):
    els = []
    i = 0

    print(driver.title)
    while not els and i < 10:
        els = driver.find_elements_by_class_name("panel-title")
        i += 1
        print(i)
        sleep(1)

    result = ''
    for el in els:
        if 'Tax account number' in el.text:
            result = el.text
            break

    if result:
        i = result.find('Tax account number')
        result = str(int(result[i::].split(':')[1]))

    return result

def get_mailing_address(driver, parcel_num):
    # Find tax_account_number
    # tax_account_num = get_tax_account_num(driver)
    # tax_account_num = '3223049074'
    # details_id = 'collapse%s' % tax_account_num

    # try:
    #     el = _find_element_by_id(driver, details_id)
    #     mailing_address = ''
    #     lines = el.text.split('\n')
    #     for i,l in enumerate(lines):
    #         if 'Mailing address' in l:
    #             mailing_address = '%s, %s' % (lines[i+1], lines[i+2])
    # except Exception as e:
    url = 'https://payment.kingcounty.gov/Home/TenantCall?app=PropertyTaxes'
    cookies = _get_cookies(driver)
    data = '{"path": "RealProperty/%s", "captchatoken":""}' % (parcel_num)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://payment.kingcounty.gov/Home/Index?app=PropertyTaxes',
        'Content-Type': 'application/json',
    }
    result = requests.post(url, cookies=cookies, headers=headers, data=data)
    result = json.loads(result.json())
    mailing_address = '%s, %s' % (
        result['data']['address1'],
        result['data']['address2'])

    return mailing_address

driver = setup_driver()
launch_tax_assessor(driver)
search_by_address(driver, '18610 4th Ave S', 'Burien', '98148')
parcel_num = get_parcel_num_by_url(driver)

goto_property_detail(driver)
# parcel_id = get_parcel_id(driver)
land_data = get_land_data(driver)
building_data = get_building_data(driver)
tax_historical_data = get_tax_historical_data(driver)

# Switch sites
launch_property_tax_site(driver)
search_tax_account_num(driver, parcel_num)
mailing_address = get_mailing_address(driver, parcel_num)

driver.close()

# printout
print('Parcel Number: %s' % parcel_num)
print('Owner Mailing Address: %s' % mailing_address)
print(land_data)
print(building_data)
print(tax_historical_data)
