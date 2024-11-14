#!/bin/env python3

#Copyright (C) <2024>  <Tobias Cruz de Melo>

from PIL import Image
import os, sys, signal

DEFAULT_X = 28
DEFAULT_Y = 34



#params for Simon pics = (p_x = 28, p_y = 34) -> explain the default parameters


def ask(question:str):
    """
    Input the question
    return  - True if the answer is in [yes.values()]
            - False if in [no.values()]
            - else "Undefined" as an error
    """
    yes = ['yes','oui','y','o']
    no = ['no','n','non']
    answer = input(question+'[Y/n]\n>>>').lower()
    if answer in yes:
        return True
    elif answer in no:
        return False
    else:
        return 'Undefined'

class Wizard():
    """Class for cropping pictures"""
    def __init__(self,params:dict) -> None:
        self.is_folder = os.path.isdir(params["entry"])
        self.input_filename = params['entry']
        self.output_filename = params['outry']
        self.img = None
        self.p_x = params['p_x'] if params['p_x']!=-42 else DEFAULT_X
        self.p_y = params['p_y'] if params['p_y']!=-42 else DEFAULT_Y
        self.overwrite = params['overwrite']
        self.auto_close = False
        self.help_required = params['help']
        signal.signal(signal.SIGINT, self.int_handling) #binding the interruption signal handler
        if self.help_required:
            Wizard.usage()
            self.auto_close = True
            self.int_handling(420,69)
        if params['licence']:
            self.print_licence()
            self.auto_close = True
            self.int_handling(420,69)

    def int_handling(self,sig_n, frame):
        """Handler of the interruption signal SIGINT or "Ctrl-C" """
        if self.auto_close:
            if self.img:
                self.img.close()
            print("Bye-Bye")
            sys.exit(0)
        choice = ask("Do you want to abort the mission ?")
        if choice: #handle True and 'Undefined'
            print("Bye-Bye")
            sys.exit(0)
        else:
            print("Then please delete my previous work in the out_folder, it might disrupt my workflow")
            x = ask("Is the folder gone ?")
            if x:
                self.main()
            else:
                print("Why ?")
                self.auto_close = True
                self.int_handling(2,[42,23,37,11,7,32,19])

    def usage():
        """Help for user"""
        helptxt = f'Usage : python3 {os.path.split(sys.argv[0])[1]} [Input] [Output] -arguments'
        helptxt += "\n\nThis python script help you crop PNG pictures :"
        helptxt += '\n\t- If you want to use it for a single picture, Input should be an existing PNG file and output a file name'
        helptxt += '\n\t- If you want to use it for a folder processing, Input should be an existing folder with PNG files in it (The script taking all the PNG files in the folder) and Output a folder name'
        helptxt += "\n\n\tArguments : "
        helptxt += "\n\t-h or --help : Print this message"
        helptxt += "\n\t-o or --overwrite: pass this argument with a folder input to overwrite the files in the folder"
        helptxt += "\n\If you want to change the parameters, here how :"
        helptxt += "\n\t-x : pass this argument as -x=20 for a 20% crop"
        helptxt += "\n\t-y : pass this argument as -y=20 for a 20% crop"
        helptxt += "\n\t--licence : print the licence of the program"

        return print(helptxt)

    def print_licence(self):
        filepath = os.path.split(__file__)[0]
        license_filep = filepath.rsplit("/",1)[0]+"/" +"LICENSE" #eliminate
        with open(license_filep,'r') as readr:
            print(readr.read())

    def func(self,filename:str,out_file_name:str,p_x:int,p_y:int):
        """Main function of the class
            Return None"""
        #checking basic condition
        if not filename.endswith('.png'):
            print('Please pass only png pictures.')
            self.auto_close = True
            self.int_handling(15,0)

        if filename == out_file_name:
            if not self.overwrite:
                print(f"Input {Filename=} and Output Filename={out_file_name}")
                changing_mind = ask("Are you sure you want to overwrite the files ?")
                if not changing_mind:
                    self.auto_close = True
                    self.int_handling(2,'sigma')
                if changing_mind == 'Undefined':
                    print('go FF 15')
                    self.auto_close = True
                    self.int_handling(2,'sigma')
                else :
                    self.overwrite = True

        if self.p_x>=100:
            print("This isn't possible as the result would be a vertical line but here you are")
            p_x = 99
        if self.p_y>=100:
            print("This isn't possible as the result would be a horizontal line but here you are")
            p_y = 99

        #Correction on the percentage as we work on each side since we don't move the center.
        p_x //= 2
        p_y //= 2

        try:
            with Image.open(filename) as self.img:
                width, height = self.img.size
                left = (p_x/100)*width
                right = width - (p_x/100)*width
                top = (p_y/100)*height
                bot = height-(p_y/100)*height
                res = self.img.crop((left,top,right,bot))
                res.save(out_file_name)
            self.img = None

        except FileNotFoundError:
            print(f"The file {filename} does not exist.. I'm closing the processus")
            self.auto_close = True
            self.img = None
            self.int_handling(2,[42,23,37,11,7,32,19])

    def load_parameters(args:list)->dict:
        """Parse the system argument values list
            Return the dict for the initialisation of the class"""
        overwrite_mode = '-o' in args or '--overwrite' in args
        help_mode = '-h' in args or '--help' in args
        licence_mode = '--licence' in args
        #print(f"load_parameters:{args=}")
        p_x = [i for i in args if i.startswith('-x')]
        if len(p_x)>0:
            p_x = p_x[0].split('=')
            p_x = int(p_x[1])
        else:
            p_x = -42

        p_y = [i for i in args if i.startswith('-y')]
        if len(p_y)>0:
            p_y = p_y[0].split('=')
            p_y = int(p_y[1])
        else:
            p_y = -42

        res = {"entry":args[1],
               "outry":args[1] if overwrite_mode else args[2],
               "p_x":p_x,
               "p_y":p_y,
               'overwrite': overwrite_mode,
               'help':help_mode,
               'licence':licence_mode
               }
        return res

    def main(self):
        """Handle the main processus with the case disjunction on the argument type [filename, folder]
            Return None"""
        if self.is_folder:
            self.folder_func()
        else:
            self.func(self.input_filename,self.output_filename,p_x=self.p_x,p_y=self.p_y)

    def folder_func(self):
        """Handle the function call for each file ending with png in the folder
            Return None"""
        if not os.path.exists(self.output_filename):
            os.makedirs(self.output_filename)
        original_filenames = [file for file in os.listdir(self.input_filename) if file.endswith('.png')] #getting the PNG's filenames
        input_filenames = [os.path.join(self.input_filename,filename) for filename in original_filenames]
        if self.overwrite:
            output_filenames = [os.path.join(self.output_filename,file_name) for file_name in original_filenames]
        else:
            output_filenames = [os.path.join(self.output_filename,'Processed_'+file_name) for file_name in original_filenames]
        for input_filename,output_filename in zip(input_filenames,output_filenames):
            self.func(filename=input_filename,out_file_name=output_filename,p_x=self.p_x,p_y=self.p_y)


def main():
    if len(sys.argv)==1:
        Wizard.usage()
        sys.exit(0)
    if len(sys.argv)==2:
        Wizard.usage()
        sys.exit(0)
    else:
        args = Wizard.load_parameters(sys.argv)
        Nbdy = Wizard(args)
        Nbdy.main()

if __name__ == "__main__" :
    main()
