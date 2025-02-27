import sys
import os
import argparse
import argcomplete
import json
import textwrap
from provisionpad.db.database import load_database
from provisionpad.runs.create_instance import create_instance
from provisionpad.runs.terminate_instance import terminate_instance
from provisionpad.runs.stop_instance import stop_instance
from provisionpad.runs.start_instance import start_instance
from provisionpad.runs.create_vpc import create_vpc
from provisionpad.runs.initiate import initiate
from provisionpad.runs.status import show_status

shut_down_time = 10

from argparse import RawTextHelpFormatter

class PPAD(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='A very simple command line tool to control'
                        'your remote cloud based workstation',
            usage='''%(prog)s <command> [<args>]

The following commands are available:
    initiate   :   Initiate your test environment; only use it once
    create     :   Create a new computing instance
    terminate  :   Terminate the already running instance
    stop       :   Stop the running instance
    start      :   Start an stopped instance
    stat       :   Get the information on the current workspace
''')
        parser.add_argument('command', help='Choose one of (initiate, create, terminate, stop, start, stat) to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def get_env_vars(self):
        home = os.path.expanduser("~")
        env_dir = os.path.join(home, '.provisionpad') 
        env_var_path = os.path.join(env_dir, 'env_variable.json')
        with open(env_var_path, 'r') as f:
            env_vars = json.load(f)
            if env_vars['env_path'] != env_var_path:
                print ('something wrong')
                raise ('The environment variable seems to be a wrong one')
        env_vars = {str(key):str(val) for key, val in env_vars.items()}
        return env_vars

    def initiate(self):
        initiate()

    def create(self):

        env_vars = self.get_env_vars()
        DB = load_database(env_vars['db_path'])

        parser = argparse.ArgumentParser(
            description='Create a new computing instance',
            usage='''propad create [option]s

If no name is provided an automatic name starting with box will be used.
Please note you can not use names starting with box.
If no instance type is provided the default t2.micro will be sued for aws
as the instance type qualifies for the free tier            
            
''')

        parser.add_argument('name', nargs='?', help='Enter the name you want to use')
        parser.add_argument('type', nargs='?', help='''Enter the type of computing instance
                                                    If you are using AWS see the following link for further info:
                                                    https://aws.amazon.com/ec2/pricing/on-demand/
                                                    ''')

        args = parser.parse_args(sys.argv[2:])

        if not args.name:
            boxname = ''
        else:
            boxname = args.name
        
        if not args.type:
            boxtype = 't2.micro'
        else:
            boxtype = args.type

        create_instance(boxname, boxtype, shut_down_time, env_vars, DB)

    def terminate(self):

        env_vars = self.get_env_vars()
        DB = load_database(env_vars['db_path'])

        parser = argparse.ArgumentParser(
            description='Create a new computing instance',
            usage='''propad terminate thename

for example:
    propad terminate box2 
    the command above will terminate the box2 and the associated root volume           
            
''')

        parser.add_argument('name', nargs='?', help='Enter the name of the box you want to terminate')

        args = parser.parse_args(sys.argv[2:])
        boxname = args.name
        if not boxname:
            raise NameError('You need to enter the name of the box')
        terminate_instance(boxname, env_vars, DB)
    
    def stop(self):

        env_vars = self.get_env_vars()
        DB = load_database(env_vars['db_path'])

        parser = argparse.ArgumentParser(
            description='Create a new computing instance',
            usage='''propad stop thename

for example:
    propad top box2 
    the command above will stop the box2 and the associated root volume           
            
''')

        parser.add_argument('name', nargs='?', help='Enter the name of the box you want to terminate')

        args = parser.parse_args(sys.argv[2:])

        boxname = args.name
        if not boxname:
            raise NameError('You need to enter the name of the box')

        stop_instance(boxname, env_vars, DB)
    
    def start(self):

        env_vars = self.get_env_vars()
        DB = load_database(env_vars['db_path'])

        parser = argparse.ArgumentParser(
            description='Create a new computing instance',
            usage='''propad stop thename

for example:
    propad start box2 
    the command above will restart the stopped box2            
            
''')

        parser.add_argument('name', nargs='?', help='Enter the name of the box you want to terminate')

        args = parser.parse_args(sys.argv[2:])

        boxname = args.name
        if not boxname:
            raise NameError('You need to enter the name of the box')

        start_instance(boxname, env_vars, DB)


    def stat(self):
        '''
        Prints out the stat of the running and stopped instances
        '''

        env_vars = self.get_env_vars()
        DB = load_database(env_vars['db_path'])
        show_status(env_vars, DB)

        
def main():
   PPAD() 



