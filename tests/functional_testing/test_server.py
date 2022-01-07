from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


def test_story():
    safari = webdriver.Safari()
    safari.get('http://127.0.0.1:5000/')
    title = safari.find_element(By.TAG_NAME, 'h1').text
    assert 'Registration Portal' in title
    assert safari.current_url == 'http://127.0.0.1:5000/'
    sleep(1)
    email = safari.find_element(By.ID, 'email')
    email.send_keys('john@simplylift.co')
    sleep(1)
    safari.find_element(By.TAG_NAME, 'button').click()
    sleep(1)
    assert safari.current_url == 'http://127.0.0.1:5000/showSummary'
    safari.find_element(By.LINK_TEXT, 'Book Places').click()
    sleep(1)
    error = safari.find_elements(By.TAG_NAME, 'li')[0].text
    assert 'Sorry this competition is too old' in error
    assert safari.current_url == 'http://127.0.0.1:5000/' \
                                 'book/Spring%20Festival/Simply%20Lift'
    safari.close()
