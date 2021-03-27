  # Used to bypass IP-ban
from stem import process as tpr
from stem import util
from stem import control as con
from stem import Signal

from time import sleep

import os

import requests as req



def get_tor_path():
    def win_gtp():
        Command = 'tor.exe'
        
        # alias for brevity
        env = lambda var, default="": os.environ.get(var,default)
        
        # Try several locations: 
        possible_locations = [
            # Under programfiles
            f'{env("PROGRAMFILES")}\\Tor\\',
            f'{env("PROGRAMFILES(X86)")}\\Tor\\',
            f'{env("PROGRAMFILES")}\\Vidalia Bundle\\Tor\\',
            f'{env("PROGRAMFILES(X86)")}\\Vidalia Bundle\\Tor\\',
            # Tor Browser, installed on desktop
            f'{env("USERPROFILE")}\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\',
            # Custom path for my dumb install
            #f'D:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\',
            # bin-stored executable  
            f'{os.getcwd()}\\bin\\tor-nt\\'
        ]
        for path in possible_locations:
            print("Trying:", path+Command)
            if os.access( path + Command, os.X_OK):
                return path + Command
        raise OSError("Could not find tor executable!")

    def posix_gtp():
        raise NotImplementedError("gotta finish this at some point.")
    # --- End of platform specific code ---
    if os.name == "posix":
        return posix_gtp()
    elif os.name == "nt":
        return win_gtp()
    elif os.name == "java":
        raise NotImplementedError("I don't know what the 'java' platform is suposed to be,"
                                  " so there's nothing here.")
    else:
        raise ValueError(f"Unregistered OS {os.name}")

        
def find_process(Command):
    def win_fp(Command):
        
        search = os.popen('wmic process get Name,ProcessId')
        results = search.read().splitlines()
        processes = [tuple([i.strip() for i in proc.strip().rsplit(' ',1)]) 
                     for proc in results[1:] if proc]
        for proc in processes:
            if proc[0] == Command:
                return proc
        return None
    def posix_gtp():
        raise NotImplementedError("gotta finish this at some point.")
    # --- End of platform specific code ---
    if os.name == "posix":
        return posix_fp(Command)
    elif os.name == "nt":
        return win_fp(Command)
    elif os.name == "java":
        raise NotImplementedError("I don't know what the 'java' platform is suposed to be,"
                                  " so there's nothing here.")
    else:
        raise ValueError(f"Unregistered OS {os.name}")

# Automaticaly find the ports for a selected PID
def identify_ports(pid):
    raise NotImplementedError("Haven't done this yet. Specify your ports manualy")
    def win_port(pid):    
        # It'll use something like this command:
        search = os.popen('netstat -aon')
        # It'll spit out a list of associated open ports
        return ports
        

def start_process(tor_cmd = None, control_port = 9051, socks_port = 9050,OtherParams=dict()):
    if tor_cmd is None:
        tor_cmd = get_tor_path()
    config = {'ControlPort':str(control_port),
              'SocksPort' : str(socks_port),
              'Log': ['NOTICE stdout'],
              **OtherParams}
    
    tor_process = tpr.launch_tor_with_config( config,
                                  tor_cmd=tor_cmd,
                                  take_ownership=True, 
                                  close_output=True)
    return tor_process
    
    

def make_session(control_port=9051, socks_port=9050, OtherParams=dict()):
    p = find_process('tor.exe')
    if p is None:
        print("started process.")
        tor_process =start_process(None,control_port,socks_port, OtherParams)
    else:
        print("found process with PID",p[1])
        tor_process = p
    print("Tor linked. Confirming connectivity.")
    
    
    session = req.Session()
    session.proxies = {}
    print("\nLOCAL IP IS:")
    print(req.get("http://httpbin.org/ip").text,"\n\n\n")
    print('Configuring socks...')
    session.proxies['http'] = f'socks5h://localhost:{socks_port}'
    session.proxies['https'] = f'socks5h://localhost:{socks_port}'
    session.headers['User-agent'] ='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    session.cookies.get_policy().set_allowed_domains([])
    print("REMOTE IP IS:")
    page=session.get("http://httpbin.org/ip", timeout=5)
    print(page.status_code,page.text,sep='\n')
    return session, tor_process

def new_route(control_port=9051, socks_port=9050):
    tor=  con.Controller.from_port(port=control_port) 
    # Authenticate
    print("Authenticating...")
    tor.authenticate()

    # Generate session:
    session = req.Session()
    session.proxies = {}
    print('Configuring socks...')
    session.proxies['http'] = f'socks5h://localhost:{socks_port}'
    session.proxies['https'] = f'socks5h://localhost:{socks_port}'

    # Print old IP
    print("OLD IP IS:")
    current_conn=session.get("http://httpbin.org/ip", timeout=5)
    print(current_conn.status_code, current_conn.text, sep='\n')

    if not tor.is_newnym_available():
        secs = tor.get_newnym_wait()
        print(f"Unable to change ID at this time, wait {secs} seconds")
        return

    print("Changing route...")
    tor.signal(Signal.NEWNYM)
    streams = tor.get_streams()
    print(f"Closing {len(streams)} streams")
    for stream in streams:
        tor.close_stream(stream.id)
    tor.clear_cache()
    print("Route Changed.")

    tor.new_circuit(await_build=True)
    print("Added a circuit")


    print("NEW IP IS:")

    new=session.get("http://httpbin.org/ip", timeout=5)
    print(new.status_code, new.text, sep='\n')

    return session
