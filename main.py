#import os - commenting out because it appears to be unused.
from re import sub
import zpl
import PySimpleGUI as sg
from zebra import Zebra
from datetime import datetime
# Commenting out because we're doing the string ourselves
#import base64
calendar = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAJ8SURBVEhLtVNdbxJBFPUn+GiMfbFVTAoxJo1oKqDvFH9X42v7CP0DNgUWlV1YTFFjYqJpKjY+WkTbla/lY7e2PFzvvTsrMwWESLjJyZ6ZnLnnztndK7DgGmtQ3H8LxfI7sZpepDcn6Mca5AwTNKMkVtMrh1rNeC1WaikG7uFH+Lm2AuZBBUqHX6EWvA7H91cYVQGZE2qr11hrHhzBj7WbcPb5k+jmlWJwHA2BFV2FzecZ2NzNgPXkLpxuROAk/sjDhngKfoqwHt+DZ7tp1KfBigShGguJbl4pBjWcqBK+DdupFGylduAoHAArgQZkMgZWIgqVBwHYSiZhO7kDX8J3sMct0c0rxeA7Nq/F12E/dAOxhJwmHd/cB2nKwSWhX+cecikG1fAyR1JPxKD+NMYR/I1kElgf9fTxCL6Xf9zg2/JVqD0MzAXqIZdiUEc05wT1kEsxsFo2NGwb7L7DaNgdwd2ZudVqi25eXTJoo7APWb3I6P++8HjehP75BWg+n7DfRqOZDDTdxAMFPDyAHB7M5tGMuF5AXkJ+PrKvIadbTDWgazo4IR1sYlzEHZzS2x/gvs8v7w+Q27PeoMjgKHAyn2eMIZc1/j69ixkNpIj4+ib0KBZqSrnjxGyAmh5riBfxHfxnRMNYhlHQ5I7gw7jmjEjepyd/adjY51Nf8i/fAJtm8wZPq4mI6MvRKGvmtE8x+tzT0FnqIZdicFJvQLPTRaHDeXo/ncuoY0TeD+Ugl39GT0P6ZqfDPeRSDMrvP0Cr24Ou60LHGUV3Aue1e8Zn32APuRSDeqMJmVcF2MvpsPfCQOQRPh9dp5nrkGa9DpmXBveQSzFYRC3YAOAPDIPyopzQJQ4AAAAASUVORK5CYII='

z = Zebra()
q = z.getqueues()
sg.theme('BlueMono')
POPUP_CENTER_X = 200
POPUP_CENTER_Y = 50

layout = [
    # Give everything keys so you're not having to fumble with things like values[0] later.
    # Also make sure they have good naming so they're easy to spot
    # enable_events=True means that every time the element is interacted with (something typed into the input box, for example),
    # it fires an event with that key name.
    [sg.Text('RMA#:', size=(20, 1)), sg.Input(key='-RMAInput-', enable_events=True)],
    [sg.Text('Number of Pallets:', size=(20, 1)), sg.Input(key='-NumPallets-', enable_events=True)],
    [sg.Text('Client:', size=(20, 1)), sg.Input(key='-Client-', enable_events=True)],
    #[sg.Text('Date Received:', size=(20, 1)),sg.Input(key='-Date-', disabled=True, use_readonly_for_disable=False), sg.CalendarButton('', image_data=calendar, close_when_date_chosen=True, target='-Date-', location=(0,0), no_titlebar=False, format='%m/%d/%Y')],
    [sg.Text('Date Received:', size=(20, 1)),sg.Input(key='-Date-', disabled=True, use_readonly_for_disable=False), sg.Button('', image_data=calendar, key='-ChooseDate-')],
    [sg.Text('Choose Printer', size=(20, 1))],
    [sg.Combo(q, key='-Printer-',readonly=True)],
    [sg.Button('Generate Label'), sg.Button('Clear'), sg.Exit()]
]

window = sg.Window('RMA Pallet Sticker Creator', layout, keep_on_top=True, enable_close_attempted_event=True)

# Good practice to enclose all main code in a "main" function (see end of script)
def main():
    while True:

        event, values = window.read()

        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'Exit') and sg.popup_yes_no('Are you sure you want to quit?',title='',location=window.CurrentLocation(), relative_location=(POPUP_CENTER_X,POPUP_CENTER_Y),keep_on_top=True) == 'Yes':
            break

        elif event == 'Clear':
            for x in ['-RMAInput-','-NumPallets-','-Client-','-Date-']:
                window[x].update('')

        #Prevents more than 25 characters in the RMA field by filling the field with a substring of the value (only the first 25 characters)
        elif event == '-RMAInput-' and values['-RMAInput-'] and len(values['-RMAInput-']) > 20:
            window['-RMAInput-'].update(values['-RMAInput-'][:-1])

        elif event == '-Client-' and values['-Client-'] and len(values['-Client-']) > 16:
            window['-Client-'].update(values['-Client-'][:-1])

        elif event == '-NumPallets-' and values['-NumPallets-']:
            # Uses some regex to prevent anything except numbers from being entered into the
            # field, and also checks to make sure the length isn't > 3 (nobody is going to print
            # that many labels)
            window['-NumPallets-'].update(sub("[^0-9]","",values['-NumPallets-']))
            if len(values['-NumPallets-']) > 3:
                window['-NumPallets-'].update(values['-NumPallets-'][:-1])
        
        elif event == '-ChooseDate-':
            date = sg.popup_get_date(location=window.CurrentLocation(), relative_location=(POPUP_CENTER_X,POPUP_CENTER_Y), close_when_chosen=True, no_titlebar=False)
            if date:
                window['-Date-'].update(f'{date[0]}/{date[1]}/{date[2]}')

        elif event == 'Generate Label':
            err = False
            for k,v in {"-RMAInput-": "RMA#", "-NumPallets-": "Number of Pallets", "-Client-": "Client", "-Date-": "Date", "-Printer-": "Printer"}.items():
                if not values[k]:
                    # The use of location and relative_location here makes the popup window always "centered" (more or less)
                    # to the main window, even if they move the window elsewhere, to another monitor, etc.
                    sg.popup(f'Please Enter {v}.', keep_on_top=True, location=window.CurrentLocation(), relative_location=(POPUP_CENTER_X,POPUP_CENTER_Y))
                    err = True
                    break
            if err:
                continue

# No need to close the window, they may want to print more.
# Generally GUIs should never be closed except by the user.
#    window.close()
            RMA = values['-RMAInput-'].upper()
            Pallet_num = values['-NumPallets-']
            Client = values['-Client-'].upper()
            Receive_Date = values['-Date-']
            z.setqueue(values['-Printer-'])
            z.setup()
            labels = []
            for x in range(int(Pallet_num)):

                # Corrected the label height/width, although it doesn't seem to have an impact either way
                l = zpl.Label(76,51)
                bar_x = 5
                if len(RMA) > 17:
                    rma_font = 3.5
                else:
                    rma_font = 4
                    bar_x = 10

                bar_width = 5 - 0.9 * (len(RMA) - 20)

                l.origin(26,0)
                l.write_text(RMA, char_height=5, char_width=rma_font, line_width=50, orientation='R', justification='C')
                l.endorigin()

                # The 2nd parameter is for the x coordinate, not sure why bar_height was used here
                l.origin(17, bar_width)
                l.barcode('C', RMA, height=90, orientation='R', print_interpretation_line='N')
                l.endorigin()

                l.origin(11, 0)
                l.write_text(f'PALLET {x + 1} OF {Pallet_num}', char_height=4, char_width=5, line_width=50, justification='C', orientation="R")
                l.endorigin()

                l.origin(6, 0)
                l.write_text(Client, char_height=4, char_width=5, line_width=50, justification='C', orientation='R')
                l.endorigin()

                l.origin(1, 0)
                l.write_text(Receive_Date, char_height=4, char_width=5, line_width=50, justification='C', orientation='R')




                label = l.dumpZPL()
                labels.append(label)
                #l.preview()

            for i in range(len(labels)):
               z.output(labels[i])

# In a nutshell, the variable "__name__" is the string "__main__" when it is run directly
# by the python interpreter, but *not* when it is imported by another script.
# This prevents code inside the "main" function from being accessible when imported,
# and is generally considered good practice.
# For more information, see: https://realpython.com/if-name-main-python/
if __name__ == "__main__":
    main()