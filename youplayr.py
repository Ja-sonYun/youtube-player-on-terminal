from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import curses

class Parser:
    def __init__(self, is_headless):
        options = webdriver.ChromeOptions()
        CHROMEDRIVER_PATH = '/Users/jasonyun/.chromedriver'
        self.YOUTUBE_PATH = 'https://www.youtube.com'
        if(is_headless):
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
        self.wait = WebDriverWait(self.driver, 3)
        self.presence = EC.presence_of_element_located
        self.visible = EC.visibility_of_element_located
        self.html = ''
        self.titles = []
        self.selected = None
        self.status = ''
        self.actions = ActionChains(self.driver)

        self.PLAY_BUTTON_PATH_TITLE = "'Play (k)'"
        self.PAUSE_BUTTON_PATH_TITLE = "'Pause (k)'"

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

    def play_music(self, debug, _id = None):
        if(_id != None): self.select_music_by_id(_id)

        self.driver.get(self.YOUTUBE_PATH+'{}'.format(str(self.selected['href'])))

        while(True):
            try:
                status = self.driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button']").get_attribute("aria-label")
                status = 'playing' if self.PAUSE_BUTTON_PATH_TITLE == status else 'paused'
                break
            except:
                sleep(0.5)

        if(status == 'paused'):
            try:
                self.driver.find_element_by_xpath("//button[@title='Play (k)']").click()
            except:
                sleep(0.5)
        while(True):
            try:
                self.driver.find_element_by_xpath("//div[@class='ytp-title-text']/a[text()[contains(., '"+self.get_name_from_title(self.selected)+"')]]")
                normal = True
            except:
                normal = False
            try:
                self.driver.find_element_by_xpath("//div[@class='ytp-ad-player-overlay']")
                is_advertising = True
                debug('found advertise')
            except:
                is_advertising = False
            if(normal or is_advertising): break
            sleep(0.5)

        while(is_advertising):
            try:
                self.driver.find_element_by_xpath("//div[@class='ytp-title-text']/a[text()[contains(., '"+self.get_name_from_title(self.selected)+"')]]")
                break;
            except:
                try:
                    self.driver.find_element_by_xpath("//button[@class='ytp-ad-skip-button ytp-button']").click()
                    debug('processed advertise')
                except:
                    sleep(0.5)

        while(True):
            try:
                status = self.driver.find_element_by_xpath("//button[@class='ytp-play-button ytp-button']").get_attribute("aria-label")
                status = 'playing' if self.PAUSE_BUTTON_PATH_TITLE == status else 'paused'
                break
            except:
                sleep(0.5)

        if(status == 'paused'):
            try:
                self.driver.find_element_by_xpath("//button[@title='Play (k)']").click()
                status = 'playing'
            except:
                sleep(0.5)

        debug('-----Done------')

        self.status = status

    def music_toggle():
        self.actions.send_keys('k')
        self.actions.perform()
        if(self.status == 'playing'): self.status == 'paused'
        else: self.status == 'playing'

    @staticmethod
    def get_name_from_title(title):
        return title.find('yt-formatted-string').string

    def get_current_status(self):
        self.html = self.driver.page_source
        soup = BeautifulSoup(self.html, 'html.parser')
        status = soup.find_all('button').find(class_='ytp-play-button ytp-button')
        return status

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

                if cmd[:4] == "quit" or cmd[0] == 'q': break

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
        while True:
            c = self.stdscr.getkey()
            if c == "k":
                current_cur = current_cur - 1 if current_cur > 0 else current_cur

            elif c == "j":
                current_cur = current_cur + 1 if current_cur < len(parser.titles)-1 else current_cur

            elif c == "q":
                self.list_up_music(4, 4, parser.titles, -1)
                break

            elif c == "\n":
                self.clear_box()
                parser.play_music(self.console_log, current_cur)
                self.music_player_loop(parser)
                break

            self.list_up_music(4, 4, parser.titles, current_cur)

    def music_player_loop(self, parser):
        self.print_player_title(Parser.get_name_from_title(parser.selected))
        self.print_player_border()
        self.stdscr.timeout(300)
        while True:
            self.print_player_status(parser.status)
            self.print_player_progress_bar(parser.get_progress_as_percent())

            self.stdscr.refresh()

            c = self.stdscr.getch()
            if c == 'k':
                parser.music_toggle()
            elif c == 'q':
                self.clear_box()
                break


    def print_player_progress_bar(self, percent):
        percentage = int(percent[:-1]) + 1
        progress_bar_size = self.cols - 19
        progress_bar_loaded = '=' * (int(float(percentage / progress_bar_size) * 100))
        progress_bar_unload = '_' * (int(progress_bar_size)-int(float(percentage / progress_bar_size) * 100))
        progress_bar = progress_bar_loaded + progress_bar_unload
        self.stdscr.addstr(8, 10, progress_bar)

    def print_player_status(self, status):
        self.stdscr.addstr(10, int(self.cols/2)-3, status)

    def print_player_title(self, title):
        self.stdscr.addstr(6, int((self.cols/2)-(len(title)/2)), title)

    def print_player_border(self):
        self.stdscr.addstr(4, 4, '-'*(self.cols-8))
        self.stdscr.addstr(13, 4, '-'*(self.cols-8))

    def list_up_music(self, y, x, titles, highlight_at):
        max_size = self.cols - 8
        self.stdscr.addstr(y, x+2, '* result *', curses.color_pair(2) | curses.A_BOLD)
        y = y + 2
        for i, title in enumerate(titles):
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
        self.stdscr.addstr(0, 0, log)
        self.stdscr.refresh()

    def console_input(self, y, x):
        curses.echo()
        curses.curs_set(1)
        self.stdscr.addstr(y, x, ' ' * (20))
        self.stdscr.refresh()
        self.stdscr.addstr(y, x, '> ')
        _input = self.stdscr.getstr(y, x+2, 20)
        curses.curs_set(0)
        curses.noecho()
        return _input.decode("utf-8")

def main(stdscr):
    parser = Parser(True)
    screen = Screen(stdscr)
    screen.loop(parser)

curses.wrapper(main)
