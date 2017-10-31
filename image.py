from PIL import Image
from io import BytesIO


def save_captcha_image(driver, filename):
    SIPAC = 'https://www.receita.fazenda.gov.br/Aplicacoes/SSL/ATFLA/Sipac.App/'
    if driver.current_url == SIPAC is False:
        raise ValueError('Sipac não está carregado no browser.]')
    captcha = crop_captcha(driver)
    captcha.save(filename)


def take_screenshot(driver):
    im = BytesIO(driver.get_screenshot_as_png())
    return Image.open(im)


def get_captcha_location(driver):
    CAPTCHA_ID = 'imgcaptcha'
    captcha = driver.find_element_by_id(CAPTCHA_ID)
    location = captcha.location_once_scrolled_into_view
    return location


def crop_captcha(driver):
    location = get_captcha_location(driver)
    screenshot = take_screenshot(driver)

    #driver.execute_script(f'window.scrollTo(0, {location["y"]})')


    CAPTCHA_WIDTH, CAPTCHA_HEIGHT = 180, 50
    CAPTCHA_IMAGE = (location['x'],
                     location['y'],
                     location['x'] + CAPTCHA_WIDTH,
                     location['y'] + CAPTCHA_HEIGHT)

    captcha = screenshot.crop(CAPTCHA_IMAGE)
    return captcha
