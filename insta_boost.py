
import os

import config


def turn_off_notification_option():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    mobile_emulation = {"deviceName": "iPhone X"}
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    return chrome_options


class InstaBoost:

    def __init__(self):
        self.browser = webdriver.Chrome(chrome_options=turn_off_notification_option())
        self.browser.maximize_window()

    def login(self, password, username):
        self.browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
        assert "Instagram" in self.browser.title
        login_element = self.browser.find_element_by_name("username")
        login_element.send_keys(username)
        password_element = self.browser.find_element_by_name("password")
        password_element.send_keys(password)
        password_element.send_keys(Keys.ENTER)
        WebDriverWait(self.browser, 5).until(EC.url_changes(self.browser.current_url))

    def get_user_followers(self, username):
        self.browser.get(os.path.join('https://www.instagram.com', username))
        followers_link = self.browser.find_element_by_css_selector('ul li a span')
        followers_count = int(followers_link.text.replace(',', ''))
        followers_link.click()
        time.sleep(3)
        # followers_list = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        followers_list = self.browser.find_element_by_css_selector('section main')
        followers_list.click()
        lis = followers_list.find_elements_by_css_selector('li')
        number_of_followers_in_list = len(lis)

        # action_chain = webdriver.ActionChains(self.browser)

        # f_body = self.browser.find_element_by_xpath("//div[@class='isgrP']")
        f_body = self.browser.find_element_by_css_selector('section main')
        i = 0
        old_number_of_followers_in_list = 0
        followers = []
        while number_of_followers_in_list < followers_count:
            self.browser.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                                        f_body)

            if old_number_of_followers_in_list != number_of_followers_in_list:
                for user in lis:
                    user_link = user.find_elements_by_css_selector('a')[-1].get_attribute('title')
                    followers.append(user_link)
            old_number_of_followers_in_list = number_of_followers_in_list
            lis = followers_list.find_elements_by_css_selector('li')
            number_of_followers_in_list = len(lis)
            print(number_of_followers_in_list, old_number_of_followers_in_list, '    ', i)
            if number_of_followers_in_list == old_number_of_followers_in_list:
                time.sleep(0.5)
            i+=1


            if len(followers) == followers_count:
                break
        return followers

    def follow_with_username(self, username):
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        follow_button = self.browser.find_element_by_css_selector('section div div span span  button')
        if follow_button.text == 'Follow':
            follow_button.click()
            time.sleep(2)
        else:
            print("You are already following this user")


def main():
    page = 'g.r.u.p.p.i.r.o.v.k.a.0'

    insta_boost = InstaBoost()
    insta_boost.login(config.password, config.username)
    followers = insta_boost.get_user_followers(page)

    with open(page, 'w') as file:
        for follower in followers:
            file.write('%s\n' % follower)


if __name__ == '__main__':
    main()
