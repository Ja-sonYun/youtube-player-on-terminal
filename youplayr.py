from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import sys
import curses

class Parser:
    def __init__(self, is_headless=False):
        options = webdriver.ChromeOptions()
        CHROMEDRIVER_PATH = '/Users/jasonyun/.chromedriver'
        SAFARIDRIVER_PATH = '/usr/bin/safaridriver'
        self.YOUTUBE_PATH = 'https://www.youtube.com'
        if(is_headless):
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
        #  self.driver = webdriver.Safari(executable_path=SAFARIDRIVER_PATH)
        self.driver.set_window_size(1900, 1900)
        self.wait = WebDriverWait(self.driver, 3)
        self.presence = EC.presence_of_element_located
        self.visible = EC.visibility_of_element_located
        self.html = ''
        self.titles = []
        self.selected = None
        self.status = ''
        self.actions = ActionChains(self.driver)

        self.PLAY_BUTTON_PATH_TITLE = "Play (k)"
        self.PAUSE_BUTTON_PATH_TITLE = "Pause (k)"

    ########### Control Window ###########

    """ use this for compare selected video title and currently playing video """
    def find_title(self):
        return self.driver.find_element_by_xpath("//title").get_attribute('innerHTML')[:-10] # drop - Youtube

    """ also compare with selected video title for detect ads """
    def currently_playing_title(self):
        return self.driver.find_element_by_xpath("//div[@class='ytp-title-text']/a").get_attribute('innerHTML')

    """ when previous video is stop playing, click next video icon """
    def click_upnext_icon(self):
        self.driver.find_element_by_xpath("//a[@class='ytp-upnext-autoplay-icon']").click()

    """ skip ads button """
    def click_skip_button(self):
        self.driver.find_element_by_xpath("//button[@class='ytp-ad-skip-button ytp-button']").click()

    """ find ads area , if not exists, raise error """
    def is_ads_exists(self):
        self.driver.find_element_by_xpath("//div[@class='ytp-ad-player-overlay']")

    def toggle_volumn(self):
        self.driver.find_element_by_xpath("//button[@class='ytp-mute-button ytp-button']").click()

    def get_button_state(self):
        return self.driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button']").get_attribute("aria-label")

    def click_play_button(self):
        self.driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button']").click()

    def get_video_current_and_duration(self):
        try:
            return [self.driver.find_element_by_xpath("//span[@class='ytp-time-current']").get_attribute('innerHTML'),
                    self.driver.find_element_by_xpath("//span[@class='ytp-time-duration']").get_attribute('innerHTML')]
        except:
            return ['error','error']

    def click_setting_button(self):
        self.driver.find_element_by_xpath("//button[@title='Settings']").click()

    def music_toggle(self):
        try:
            self.driver.find_element_by_xpath("//button[@title='Play (k)']").click()
            self.status = 'playing'
        except:
            self.driver.find_element_by_xpath("//button[@title='Pause (k)']").click()
            self.status = 'Paused'
        sleep(0.5)
        self.prevent_stop_showing_bottom_bar()

    def is_setting_opened(self):
        try:
            self.driver.find_element_by_xpath("//button[@class='ytp-button ytp-settings-button']").get_attribute('aria-expanded')
            return True
        except:
            return False

    def get_current_video_title(self):
        try:
            return self.driver.find_element_by_xpath("//*[@id='container']/h1/yt-formatted-string").get_attribute('innerHTML')
        except:
            return 'not loaded'

    def get_current_status(self):
        status = self.driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button']").get_attribute("aria-label")
        self.status = 'paused' if self.PAUSE_BUTTON_PATH_TITLE == status else 'playing'

    def get_progress_as_percent(self):
        progress_float = self.driver.find_element_by_xpath("//div[@class='ytp-play-progress ytp-swatch-background-color']").get_attribute("style")
        return "{0:.0%}".format(float(progress_float[progress_float.find("(")+1:progress_float.find(")")]))

    def toggle_autoplay(self):
        try:
            self.driver.find_element_by_xpath("//button[@aria-label='Autoplay is on']").click()
        except:
            self.driver.find_element_by_xpath("//button[@aria-label='Autoplay is off']").click()

    def get_autoplay_state(self):
        try:
            self.driver.find_element_by_xpath("//button[@aria-label='Autoplay is on']")
            return True
        except:
            return False

    def next_music(self):
        try:
            self.driver.find_element_by_xpath("//a[@class='ytp-next-button ytp-button']").click()
            sleep(0.5)
            self.prevent_stop_showing_bottom_bar()
            return True
        except:
            return False

    def close_unnecessary_elements(self):
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'SKIP TRIAL')]").click()
            self.driver.find_element_by_xpath("//*[contains(text(), 'SKIP TRIAL')]").click()
        except:
            pass

    ######################################

    def __del__(self):
        self.quit()
        print("Selenium suceessfully quitted.")

    def search_in_youtube(self, keyword):
        self.driver.get(self.YOUTUBE_PATH+'/results?search_query={}'.format(str(keyword)))
        self.wait.until(self.visible((By.ID, "video-title")))

        self.titles = []
        self.html = self.driver.page_source
        soup = BeautifulSoup(self.html, 'html.parser')
        title_tags = soup.find('ytd-search') \
            .find('ytd-two-column-search-results-renderer') \
            .find('ytd-section-list-renderer') \
            .find(id='contents') \
            .find('ytd-item-section-renderer') \
            .find(id='contents') \
            .find_all('ytd-video-renderer')

        for title_tag in title_tags:
            self.titles.append(title_tag.find(id='meta').find('a'))

    def select_music_by_id(self, _id):
        self.selected = self.titles[_id]

    def is_finished(self):
        try:
            self.click_upnext_icon()
            self.prevent_stop_showing_bottom_bar()
            return True
        except:
            return False

    def pass_ads(self, debug):
        normal = False
        while True:
            debug('getting ad info', True)
            try:
                if(self.currently_playing_title() == self.find_title()):
                    normal = True
                    return
            except:
                normal = False
            try:
                self.is_ads_exists()
                is_advertising = True
                #  self.toggle_volumn()
                debug('found advertisements. skipping...')
            except:
                is_advertising = False
            if(normal or is_advertising): break
            sleep(0.5)

        count = 0
        while(is_advertising):
            if(count > 8):
                debug('fail.reloading..', True)
                self.driver.navigate().refresh()
            debug(str(count), True)
            if(self.currently_playing_title() == self.find_title()):
                normal = True
                debug('advertisement not found')
                break
            else:
                try:
                    debug('trying to skip ads')
                    self.click_skip_button()
                    break
                except:
                    try:
                        self.click_setting_button()
                    except:
                        pass
                    count = count + 1
                    sleep(1.0)

        #  if(is_advertising):
        #      while True:
        #          debug('trying to unmute', True)
        #          try:
        #              self.toggle_volumn()
        #              break
        #          except:
        #              sleep(0.2)

        #  if(self.is_setting_opened() is not True):
        #      self.click_setting_button()

    def play_music(self, debug, _id = None):
        if(_id != None): self.select_music_by_id(_id)
        debug('loading...')

        self.driver.get(self.YOUTUBE_PATH+'{}'.format(str(self.selected['href'])))

        while True:
            try:
                debug('getting button state')
                status = self.get_button_state()
                status = 'playing' if self.PAUSE_BUTTON_PATH_TITLE == status else 'paused'
                if(status == 'paused'):
                    self.click_play_button()
                break
            except:
                sleep(0.5)

        debug('checking ads exist')
        self.pass_ads(debug)

        while True:
            try:
                debug('getting button state')
                status = self.get_button_state()
                status = 'playing' if self.PAUSE_BUTTON_PATH_TITLE == status else 'paused'
                if(status == 'paused'):
                    self.click_play_button()
                break
            except:
                sleep(0.5)

        debug('almost done...')
        self.prevent_stop_showing_bottom_bar()

        self.status = status

    def prevent_stop_showing_bottom_bar(self):
        while True:
            try:
                self.click_setting_button()
                break
            except:
                sleep(0.5)

    @staticmethod
    def get_name_from_title(title):
        return title.find('yt-formatted-string').string

    def quit(self):
        self.driver.quit()

class Screen:
    """
    From main, pass stdscr to here => Screen(stdscr)
    """
    def __init__(self, stdscr):
        self.rows, self.cols = stdscr.getmaxyx()
        self.stdscr = stdscr
        self.print_area = None
        self.print_box() #  initialize print_area

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE,  curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN,   curses.COLOR_BLACK)

        curses.curs_set(0)

        self.print_header()

    def clear_box(self):
        self.print_area.erase()
        self.print_box()

    def print_box(self):
        self.print_area = curses.newwin(self.rows-4, self.cols-2, 2, 1)
        self.print_area.box()
        self.stdscr.refresh()
        self.print_area.refresh()

    def print_header(self):
        self.stdscr.addstr(1, int(self.cols/2-7), "Youtube Player", curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(1, 1, "type .{ query } to search", curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.refresh()

    def loop(self, parser):
        while True:
            try:
                cmd = self.console_input(self.rows-1, 4)
                # after get command from prompt
                if cmd == -1: continue

                elif cmd[:4] == "quit" or cmd[0] == 'q': break

                elif cmd[:4] == "help" or cmd[0] == 'h':
                    self.clear_box()

                elif cmd[0] == '.':
                    self.move_list_page_loop(parser, cmd[1:])

                else:
                    self.clear_box()
                    self.stdscr.addstr(6, 5, "wrong command.")
                    self.stdscr.refresh()

            except KeyboardInterrupt:
                break


    def move_list_page_loop(self, parser, search_string):
        self.clear_box()
        self.stdscr.addstr(6, 5, "searching...")
        self.stdscr.refresh()

        parser.search_in_youtube(search_string)

        current_cur = 0

        self.list_up_music(4, 4, parser.titles, current_cur)
        self.stdscr.timeout(100)
        while True:
            c = self.stdscr.getch()
            try:
                c = chr(c)
                self.stdscr.addstr(0, 0, c)
                if c == "k":
                    current_cur = current_cur - 1 if current_cur > 0 else current_cur
                    self.list_up_music(4, 4, parser.titles, current_cur)

                elif c == "j":
                    current_cur = current_cur + 1 if current_cur < len(parser.titles)-1 else current_cur
                    self.list_up_music(4, 4, parser.titles, current_cur)

                elif c == "q":
                    self.list_up_music(4, 4, parser.titles, -1)
                    break

                elif c == "\n":
                    self.clear_box()
                    parser.play_music(self.print_process, current_cur)
                    self.music_player_loop(parser)
                    break
            except ValueError:
                self.stdscr.addch(0, 0, ' ')

    def music_player_loop(self, parser):
        self.print_player_border()
        while True:
            parser.close_unnecessary_elements()
            parser.is_finished() #  move to next vidoe
            self.print_player_status(parser.status)
            self.print_player_progress_bar(parser.get_progress_as_percent())
            self.print_current_and_duration_time(parser.get_video_current_and_duration())
            self.print_player_title(parser.get_current_video_title())
            parser.pass_ads(self.print_process)

            self.stdscr.refresh()

            c = self.stdscr.getch()
            try:
                c = chr(c)
                if c == 'm':
                    parser.music_toggle()
                if c == 'n':
                    parser.next_music()
                elif c == 'q':
                    self.clear_box()
                    break
            except ValueError:
                pass

    def print_player_progress_bar(self, percent):
        percentage = int(percent[:-1]) + 1
        progress_bar_size = self.cols - 20
        progress_bar_loaded = '=' * (int(progress_bar_size * percentage / 100))
        progress_bar_unload = '_' * (int(progress_bar_size)-int(progress_bar_size * percentage / 100))
        progress_bar = progress_bar_loaded + progress_bar_unload
        self.stdscr.addstr(8, 10, progress_bar)

    def print_current_and_duration_time(self, cur_dur):
        self.stdscr.addstr(9, 4, ' '*(self.cols-8))
        self.stdscr.addstr(9, 9, cur_dur[0])
        self.stdscr.addstr(9, self.cols-9-len(cur_dur[1]), cur_dur[1])

    def print_process(self, info, is_log=False):
        if(is_log):
            self.console_log(info)
        else:
            self.stdscr.addstr(6, 3, ' '*(self.cols-6))
            self.stdscr.addstr(6, 6, info);
            self.stdscr.refresh()

    def print_player_status(self, status):
        self.stdscr.addstr(10, int(self.cols/2)-3, '        ')
        self.stdscr.addstr(10, int(self.cols/2)-3, status)

    def print_player_title(self, title):
        if(len(title) > self.cols-10): title = title[:-(len(title)-(self.cols-10))]+'..'
        self.stdscr.addstr(6, 3, ' '*(self.cols-6))
        self.stdscr.addstr(6, int((self.cols/2)-(len(title)/2)), title)

    def print_player_border(self):
        self.stdscr.addstr(4, 4, '-'*(self.cols-8))
        self.stdscr.addstr(12, 4, '-'*(self.cols-8))

    def list_up_music(self, y, x, titles, highlight_at):
        max_size = self.cols - 8
        self.stdscr.addstr(y, x+2, '* result *', curses.color_pair(2) | curses.A_BOLD)
        y = y + 2
        for i, title in enumerate(titles):
            if(i+y > self.rows-4): break
            self.stdscr.addstr(y+i, x-1, ' '*(max_size+1))
            title_name = Parser.get_name_from_title(title)
            if(len(title_name) > max_size):
                title_name = title_name[:max_size-2] + '..'
            if(highlight_at == i):
                self.stdscr.addch(y+i, x-1, '*')
                self.stdscr.addstr(y+i, x, title_name + ' ', curses.color_pair(1) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y+i, x, title_name + ' ')

    def console_log(self, log):
        self.stdscr.addstr(0, 0, '          ')
        self.stdscr.addstr(0, 0, log)
        self.stdscr.refresh()

    def console_input(self, y, x):
        self.stdscr.timeout(-1)
        curses.echo()
        curses.curs_set(1)
        self.stdscr.addstr(y, x, ' ' * (self.cols-12))
        self.stdscr.refresh()
        self.stdscr.addstr(y, x, '> ')
        _input = self.stdscr.getstr(y, x+2, self.cols-12)
        curses.curs_set(0)
        curses.noecho()
        return _input.decode("utf-8")

def main(stdscr):
    try:
        if(sys.argv[1] == '--headless'):
            parser = Parser(True)
    except:
        parser = Parser()

    screen = Screen(stdscr)
    screen.loop(parser)

curses.wrapper(main)
