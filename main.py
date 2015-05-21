from StringIO import StringIO
from bs4 import BeautifulSoup
from tabulate import tabulate
from colorama import init as init_colorama, Fore, Style, Back
from threading import Timer
import time
import pycurl
import click
import re
import cmd
import os
import shlex
import string

room_ids = {
    1: '1343645', 2: '134368', 3: '134365', 4: '134367', 5: '134366',
    6: '1343613', 7: '1343639', 8: '1343638', 9: '1343624', 10: '1343636',
    11: '1343637', 12: '1343670', 13: '1343672', 14: '1343671', 15: '1343669',
    16: '1343668', 17: '1343667', 18: '1343666', 19: '1343622', 20: '1343623',
    21: '134369', 22: '1343646', 23: '1343647', 24: '1343648', 25: '1343619',
    26: '1343611', 27: '1343612', 28: '1343620', 29: '1343614', 30: '1343655',
    31: '1343656', 32: '1343629', 33: '1343630', 34: '1343615', 35: '1343631',
    36: '1343644', 37: '134363', 38: '134362', 39: '134361', 40: '1343634',
    41: '1343635', 42: '1343640', 43: '1343652', 44: '1343653', 45: '1343643',
    46: '1343642', 47: '1343649', 48: '1343650', 49: '1343651', 50: '1343617',
    51: '1343616'
}

class Laundry(cmd.Cmd):
    '''Why use laundryview.com when you can use this CLI? /s
    '''

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.prompt         = "> "
        self.timer_response = ['''"Hey fuck face, your laundry is done"''', '''"Get your fucking laundry right now"''']
        self.timer          = None
        self.home           = "http://www.laundryview.com/lvs.php"
        self.room_url       = "http://classic.laundryview.com/laundry_room.php?view=c&lr="
        self.dorm_cache     = ""
        self.version        = "v1.0"
        self.logo           = '''
          _  _    _   _             _                                 _             _  _
         | \| |  | | | |    o O O  | |     __ _    _  _    _ _     __| |     _ _   | || |
         | .` |  | |_| |   o       | |__  / _` |  | +| |  | ' \   / _` |    | '_|   \_, |
         |_|\_|   \___/   TS__[O]  |____| \__,_|   \_,_|  |_||_|  \__,_|   _|_|_   _|__/
        _|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_| """"|
        "`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' '''
        self.intro          = self.logo + self.version



    def chowder(self, url, param):
        '''Given a URL, make a cURL request to get a page's contents and
        pass it to BeautifulSoup for later parsing. Wow this chowder is tasty!
        '''

        if param == 1:
            url = self.room_url + room_ids[url]

        store = StringIO()

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, store.write)
        c.setopt(c.HTTPHEADER, ['Accept: application/json'])
        c.setopt(c.VERBOSE, 0)
        c.perform()

        content = store.getvalue()
        soup    = BeautifulSoup(content)
        return soup

    def do_dorms(self, line):
        '''
        dorms - Returns the full list of dorms and their corresponding numbers
        '''

        '''If the 'dorms' command is invoked, print all dorm buildings that have
        laundry machines, and the dorm buildings' corresponding IDs
        '''

        # User is querying list of dorms for the first time. Will save the result
        # for future queries of the dorm list
        if len(self.dorm_cache) == 0:

            soup  = self.chowder(self.home, 0)
            dorms = soup.findAll(class_="a-room")
            num   = 1
            data  = []

            for dorm in dorms:

                d       = ''.join(dorm.findAll(text=True)).strip().encode("utf-8")
                id      = re.sub('[^0-9]','', dorm['href']).strip().encode("utf-8")
                headers = ["Building #", "Building Name"]

                data.append([num, d])
                num += 1

            self.dorm_cache = tabulate(data, headers=headers, tablefmt="psql")

        print self.dorm_cache

    def do_status(self, s):
        '''
        status <x> - Get status of all laundry machines in dorm number <x>
        '''

        '''Given a building #, get the status of all laundry machines for the
        building corresponding to that #. The building #s can be found by
        querying with the "dorms" command. A building # corresponds to a
        building ID as defined by laundryview.com, and can be found in the "room_ids" dictionary above
        '''

        line = s.split()

        if (len(line) > 0 and line[0].isdigit()):
            soup = self.chowder(int(line[0]), 1)

            dorm_name = soup.find(id="monitor-head").h2.contents[0].encode("utf-8")
            machines  = soup.find(id="classic_monitor").findAll(class_="desc")
            statuses  = soup.find(id="classic_monitor").findAll(class_="stat")
            data      = []

            print "\n+{}+".format("-" * (len(dorm_name) + 2))
            print "| {} |".format(Back.CYAN + Fore.WHITE + dorm_name + Back.RESET + Fore.RESET)
            print "+{}+\n".format("-" * (len(dorm_name) + 2))

            for machine, status in zip(machines, statuses):

                m = ''.join(machine.findAll(text=True)).strip().encode("utf-8")
                s = ''.join(status.findAll(text=True)).strip().encode("utf-8")

                if s != "available":
                    data.append([m, Fore.CYAN + s + Fore.RESET])
                else:
                    data.append([m, Fore.GREEN + s + Fore.RESET])

            print tabulate(data, headers=['Machine #', 'Machine Status'], tablefmt="psql")
        else:
            print "You must provide a valid building number to get the status of"

    def do_alert(self, s):
        '''
        alert <string> <string> ... - Change the default alert message(s). Must
        add at least one.
        '''

        # shlex module provides really convenient splitting of quoted string args
        line = shlex.split(s)

        if len(line) > 0:
            self.timer_response = []

            for response in line:
                r = '''{}'''.format(response)
                self.timer_response.append(r)
            print "Alert message successfully set to the following sequence: {}".format(self.timer_response)
        else:
            print "You must provide at least one response for the alert message."

    def do_timer(self, s):
        '''
        timer <x> <y> - Will alert you when laundry machine <y> has finished
        its laundry cycle in dorm number <x>
        '''

        '''Provides user with the ability to set a timer for a laundry machine.
        Notifies the user with a default or user defined audio message when the
        machine has finished its laundry cycle.
        '''

        line                 = s.split()
        timer_set            = 0
        dorm_num             = int(line[0])
        machine_num_to_check = line[1].strip()
        time_remaining       = None

        soup = self.chowder(dorm_num, 1)
        response = ""

        machines = soup.find(id="classic_monitor").findAll(class_="desc")
        statuses = soup.find(id="classic_monitor").findAll(class_="stat")

        # machines and statuses will always be the same length as each
        # machine must have a corresponding status, and vice-versa
        for x in range(0, len(machines)):

            machine_num = machines[x].text.encode("utf-8").strip()

            if machine_num == machine_num_to_check:
                print machine_num

                for y in range(0, len(statuses)):

                    machine_status = statuses[x].text.encode("utf-8").strip()

                    if "remaining" in machine_status:
                        timer_set = 1

                        # Get the time remaining on the machine, convert it to int, convert it to seconds
                        time_remaining = int(re.sub('[^0-9]', '', machine_status)) * 60
                        print "Timer has been set for machine number {} with {}".format(machine_num, machine_status)
                        break
                    else:
                        print "That machine is currently unoccupied, out of service, or currently running an extended cycle"
                        break

        # If user has set a timer, alert the user once the machine is finished
        if timer_set:
            def alert():
                '''Local function that invokes OSX's text-to-speech voice
                functionality to output the responses in timer_response
                '''
                for response in self.timer_response:
                    os.system('say ' + response)

            time_now_sec = time.time()
            sleep        = time_now_sec + time_remaining

            # Start a thread that will call the alert function after the
            # remaining time on the laundry machine has passed
            self.timer = Timer(5.0, alert)
            self.timer.start()

    def do_stop(self, line):
        '''stop - Stops any timer that was set
        '''

        '''Provides users with the functionality to stop a timer that they
        recently set
        '''

        if self.timer.isAlive():
            self.timer.cancel()
            print "Timer has been stopped."
        else:
            print "No timer has been set to stop."

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    l = Laundry()
    l.cmdloop()