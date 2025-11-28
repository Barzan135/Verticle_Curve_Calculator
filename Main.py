import PySimpleGUI as sg

import sqlite3 
con = sqlite3.connect("CurveSaveFile.db")
cursor = con.cursor()

import math
sg.theme("DarkBlue18")

button_height = 1
button_length = 30

font = "Calibri"
header_size = 16
text_size = 12

## Initialize and Set Defaults
Num_lanes = " "
Lane_Width = " "
Divided_Road = False
Shoulder_Width = " "
RoadArea = " "
CurveName = " "

curveslist = []
cursor.execute("CREATE TABLE IF NOT EXISTS Curves(Name TEXT, SSDReq REAL, SSDAvail REAL, PSDReq REAL, PSDAvail REAL, MaxSpeed REAL, DesignSpeed REAL)")

Data = cursor.execute("SELECT * FROM Curves").fetchall()
for i in range(0, len(Data)):
    print(Data)
    print("Here")
    curveslist.append(Data[i])
    print(Data[i])



 

def chainage_translation(m):
     first = int(m//100)
     second = m % 100
     return (f'{first}+{second:05.2f}'.replace(".00",""))

def location_translation(m):
     first, second = m.split("+")
     return int(first)*100+float(second)

def Error_Message(message):
     error_layout = [
          [sg.Text(message, font=(font, header_size))],
          [sg.Button("Ok")]
     ]
     ErrorWindow = sg.Window("ERROR!", error_layout)
     while True:
          event, values = ErrorWindow.read()
          if event == sg.WIN_CLOSED or event == "Ok":
               break
     ErrorWindow.Close()

def max_speed_from_table(S_avail, speed_list, dist_list):
    v_max = 0.0
    for v, d_req in zip(speed_list, dist_list):
        if d_req <= S_avail:
            v_max = v
        else:
            break
    return v_max


def calc_ssd(v_kmh, grade=0.0, t=2.5, b=3.4):
    # SSD = d1 + d2
    # d1 = 0.278 * v * t
    # d2 = v^2 / [254 * (b/9.81 + grade)]
    d1 = 0.278 * v_kmh * t
    d2 = (v_kmh ** 2) / (254.0 * (b / 9.81 + grade))
    return d1 + d2

def max_speed_from_ssd(S_avail, grade=0.0, t=2.5, b=3.4):
    # Solve SSD(v) = S_avail for v (km/h)
    k1 = 0.278 * t
    k2 = 1.0 / (254.0 * (b / 9.81 + (grade/100)))
    disc = k1 ** 2 + 4.0 * k2 * S_avail
    return (-k1 + math.sqrt(disc)) / (2.0 * k2)

# PSD

# PSD table (speed in km/h vs PSD in m)
PSD_SPEEDS = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
PSD_VALUES = [220, 290, 350, 410, 490, 550, 610, 680, 730, 800, 860]

def max_speed_from_psd(S_avail_psd):
    return max_speed_from_table(S_avail_psd, PSD_SPEEDS, PSD_VALUES)


def OutputWindow(SSDReq, SSDAvail, PSDReq, PSDAvail, MaxSpeed, DesignSpeed):
     SSDPass = "FAIL"
     SSDColour = "#ff4444"

     PSDPass = "FAIL"
     PSDColour = "#ff4444"

     SpeedPass = "FAIL"
     SpeedColour = "#ff4444"

     if SSDReq < SSDAvail:
          SSDPass = "PASS"
          SSDColour = "#00dd00"
     if PSDReq != "n/a":
          if PSDReq < PSDAvail:
               PSDPass = "PASS"
               PSDColour = "#00dd00"
     else:
          PSDPass = "N/A"
          PSDColour = "#00dd00"
     if DesignSpeed < MaxSpeed:
          SpeedPass = "PASS"
          SpeedColour = "#00dd00"

     ## time for calculations
     

     layout4=[
          [sg.Column([
               [sg.Text("Verticle Curve Results", font=(font, header_size))],
               [sg.Text(" ")], 

               [sg.Text("Sight Distance Check", font=(font, text_size))],
               [sg.Text(f'SSD Required: {SSDReq} m', font=(font, text_size))],
               [sg.Text(f'SSD Available: {SSDAvail} m', font=(font, text_size))],
               [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(SSDPass, text_color=SSDColour, font=(font, text_size))],

               [sg.Text(" ")], 
               [sg.Text(f'PSD Required: {PSDReq} m',font=(font, text_size) )],
               [sg.Text(f'PSD Available: {PSDAvail} m', font=(font, text_size))],
               [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(PSDPass, text_color=PSDColour, font=(font, text_size))],
               [sg.Text(" ", font=(font, text_size))], 

               [sg.Text("Maximum Allowable Speed", font=(font, header_size))],
               [sg.Text(f'Max Safe Speed: {MaxSpeed} km/hr', font=(font, text_size))],
               [sg.Text(f'Design Speed: {DesignSpeed} km/hr', font=(font, text_size))],
               [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(SpeedPass, text_color=SpeedColour, font=(font, text_size))],

               [sg.Text(" ", font=(font, text_size))], 
               [sg.Button("Close", font=(font, text_size)), sg.Button("Save Curve", font=(font, text_size))]
          ])]
     ]
     OutputWindow = sg.Window("CIVIL-3020 Assignment 3", layout4)
     while True:
          event, values = OutputWindow.read()
          if event == sg.WIN_CLOSED or event == "Close":
               break
          if event == "Close":
               Window2()
               break
          if event == "Save Curve":
               print(CurveName)
               cursor.execute(f'INSERT INTO Curves VALUES(?,?,?,?,?,?,?)', (CurveName, SSDReq, SSDAvail, PSDReq, PSDAvail, MaxSpeed, DesignSpeed))
               con.commit()
               print("Attempting save here")
               break
     OutputWindow.Close()
          
def Window3():
     layout3 = [
          [sg.Column([
               [sg.Text("Curve Inputs", font=(font, header_size))],
               [sg.Text("PVI Station: ", font=(font, text_size), size=(20,1)), sg.Input()],
               [sg.Text("PVI Elevation: ", font=(font, text_size), size=(20,1)), sg.Input()],
               [sg.Text("Grade In (%): ", font=(font, text_size), size=(20,1)), sg.Input()],
               [sg.Text("Grade Out (%): ", font=(font, text_size), size=(20,1)), sg.Input()],
               [sg.Text("Curve Length (m): ", font=(font, text_size), size=(20,1)), sg.Input()],
               [sg.Text("Speed & Sight Inputs", font=(font, header_size) )],
               [sg.Text("Design Speed (km/hr): ", font=(font, text_size)), sg.Input()],
               [sg.Button("Close", font=(font, text_size)), sg.Button("Back", font=(font, text_size)), sg.Button("Next", font=(font, text_size))]
          ], justification="center", element_justification="center")],
     ]
     InputWindow2 = sg.Window("CIVIL-3020 Assignment 3", layout3)
     while True:
          event, values = InputWindow2.read()
          if event == sg.WIN_CLOSED or event == "Close":
               break
          if event == "Back":
               InputWindow2.Close()
               Window2()
               break
          if event == "Next":
               for i in range(0, 5):
                    print(values[i])
               InputWindow2.Close()

               ##SSD req to be completed by nick
               v = float(values[4])
               g1 = float(values[2])
               g2 = float(values[3])
               ssd_avail = math.ceil(calc_ssd(v, max(abs(g1), abs(g2)), 2.5, 3.4))
               if float(Num_lanes) <= 2 and RoadArea == "Rural" and Divided_Road == False:
                    ## nick will calculate this for now temp value of 20
                    psd_value = 20
               else: 
                    psd_value = "n/a"
               print(max([g1,g2]))
               print(type(max([g1,g2])))
               ## calculate max speed 
               if psd_value == "n/a":
                    max_speed = math.floor(min([max_speed_from_ssd(30, max([g1, g2]), 2.5, 3.4 )])/5)*5
               else:
                    max_speed = math.floor(min([max_speed_from_ssd(30, max([g1, g2]), 2.5, 3.4 ), max_speed_from_psd(20)])/5)*5
               OutputWindow(ssd_avail, 2,  psd_value, 20, max_speed, v)
               break
          


def Window2():
     global Num_lanes
     global Lane_Width
     global Divided_Road
     global Shoulder_Width
     global RoadArea
     global CurveName
     layout2 =[
          [sg.Column([
                [sg.Text("Roadway Inputs", font=(font, header_size))],
                [sg.Text("Curve Name: ", font=(font, text_size), size=(20,1)), sg.Input(f'{CurveName}')],
                [sg.Text("Number of Lanes: ", font=(font, text_size), size=(20,1)), sg.Input(f'{Num_lanes}')],
                [sg.Text("Lane Width (m): ", font=(font, text_size), size=(20,1)), sg.Input(f'{Lane_Width}')],
                [sg.Checkbox("Divided Road?", font=(font, text_size), size=(20,1))],
                [sg.Text("Shoulder Width (m): ", font=(font, text_size), size=(20,1)), sg.Input(f'{Shoulder_Width}')],
                [sg.Text("Roadway Location", font=(font, header_size))],
                [sg.Checkbox("Urban", font=(font, text_size), size=(20,2)), sg.Checkbox("Rural", font=(font, text_size))],
                [sg.Button("Close", font=(font, text_size)), sg.Button("Back", font=(font, text_size)), sg.Button("Next", font=(font, text_size))]
            ], justification="center", element_justification="center")],
     ]


     InputWindow1 = sg.Window("CIVIL-3020 Assignment 3", layout2)

     while True:
            event, values = InputWindow1.read()
            if event == sg.WIN_CLOSED or event == "Close":
                InputWindow1.Close()
                break
            if event == "Next":
                print(values)
                CurveName = values[0]
                Num_lanes = values[1]
                Lane_Width = values[2]
                Divided_Road = values[3]
                Shoulder_Width = values[4]
                if values[5] == True and values[6] == True: 
                     Error_Message("You must select only ONE road location.")
                     continue
                if len(values[0]) <2  or len(values[1]) <2 or len(values[2]) <2  or len(values[4]) <2:
                     Error_Message("You must fill all curve data")
                     continue
                if values[5] == False and values[6] == False:
                     Error_Message("You must input a valid road location")
                     continue
                
                RoadArea = values[5] or values[6]
                InputWindow1.Close()
                Window3()
                break
            if event == "Back":
                 InputWindow1.Close()
                 Start()
                 break        
    
          
def Saved_Curves():
     rows = []
     for i in curveslist:
          rows.append([sg.Button(i[0], key=(f'open_{i[0]}'))])

     savelayout = [
          [sg.Text("Saved Curves", font=(font, header_size))],
          *rows, 
          [sg.Button("Back"), sg.Button("Close")]
      ]
     StartWindow = sg.Window("CIVIL-3020 Assignment 3", savelayout)
     while True: 
            event, values = StartWindow.read() 
            if event == sg.WIN_CLOSED or event == "Close":
                StartWindow.close()
                break
            elif event == "Back":
                 Start()
                 StartWindow.close()
            elif event.startswith("open_"):
                 curve_name = event.replace("open_", "")
                 StartWindow.Close()
                 OpenSave(curve_name)
                 print(curve_name)
                 break

def OpenSave(CurveName):
     SelectedData = None
     for i in range(len(Data)):
          if Data[i][0] == CurveName:
               SelectedData = Data[i]

     if SelectedData == None:
          Error_Message("GUI ERROR: No data found for curve!")


     ## Find curve data from datastore.
     SSDReq = SelectedData[1]
     SSDAvail = SelectedData[2]
     PSDReq = SelectedData[3]
     PSDAvail = SelectedData[4]
     MaxSpeed = SelectedData[5]
     DesignSpeed = SelectedData[6]

     ## Run as usual
     SSDPass = "FAIL"
     SSDColour = "#ff4444"

     PSDPass = "FAIL"
     PSDColour = "#ff4444"

     SpeedPass = "FAIL"
     SpeedColour = "#ff4444"

     if SSDReq < SSDAvail:
          SSDPass = "PASS"
          SSDColour = "#00dd00"
     if PSDReq != "n/a":
          if PSDReq < PSDAvail:
               PSDPass = "PASS"
               PSDColour = "#00dd00"
     else:
          PSDPass = "N/A"
          PSDColour = "#00dd00"
     if DesignSpeed < MaxSpeed:
          SpeedPass = "PASS"
          SpeedColour = "#00dd00"

     SaveLayout = [
          [sg.Text(f'Saved Curve Data: {CurveName}', font=(font, header_size))],
          [sg.Text(" ")], 

          [sg.Text("Sight Distance Check", font=(font, text_size))],
          [sg.Text(f'SSD Required: {SSDReq} m', font=(font, text_size))],
          [sg.Text(f'SSD Available: {SSDAvail} m', font=(font, text_size))],
          [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(SSDPass, text_color=SSDColour, font=(font, text_size))],

          [sg.Text(" ")], 
          [sg.Text(f'PSD Required: {PSDReq} m',font=(font, text_size) )],
          [sg.Text(f'PSD Available: {PSDAvail} m', font=(font, text_size))],
          [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(PSDPass, text_color=PSDColour, font=(font, text_size))],
          [sg.Text(" ", font=(font, text_size))], 

          [sg.Text("Maximum Allowable Speed", font=(font, header_size))],
          [sg.Text(f'Max Safe Speed: {MaxSpeed} km/hr', font=(font, text_size))],
          [sg.Text(f'Design Speed: {DesignSpeed} km/hr', font=(font, text_size))],
          [sg.Text(f'Status: ', font=(font, text_size)), sg.Text(SpeedPass, text_color=SpeedColour, font=(font, text_size))],

          [sg.Text(" ", font=(font, text_size))], 
          [sg.Button("Close", font=(font, text_size)), sg.Button("Delete", font=(font, text_size))]
     ]
     SaveDataWindow = sg.Window("CIVIL-3020 Assignment 3", SaveLayout)
     while True: 
            event, values = SaveDataWindow.read() 
            if event == sg.WIN_CLOSED or event == "Close":
                SaveDataWindow.close()
                break
            elif event == "Delete":
                 print("deleting")
                 cursor.execute(f'DELETE FROM curves WHERE Name = ?', (CurveName,))
                 con.commit()
                 SaveDataWindow.close()
                 break
           



def Start():
     Num_lanes = " "
     Lane_Width = " "
     Divided_Road = False
     Shoulder_Width = " "
     RoadArea = " "
     CurveName = " "

     layout1 = [
        [sg.Column([[sg.Text("Verticle Curve Design Tool", font=(font, header_size))]], justification = "center")],
        [sg.Column([[sg.Button("Create New Curve", size=(button_length,button_height))]], justification = "center")],
        [sg.Column([[sg.Button("View Saved Curves", size=(button_length,button_height))]], justification = "center")],
        [sg.Column([[sg.Button("Close", size=(button_length,button_height))]], justification = "center")],
    ]
     StartWindow = sg.Window("CIVIL-3020 Assignment 3", layout1)
     while True: 
            event, values = StartWindow.read() 
            if event == sg.WIN_CLOSED or event == "Close":
                StartWindow.close()
                break
            elif event == "Create New Curve":
                StartWindow.close()
                Window2()
                break
            elif event == "View Saved Curves":
                 Saved_Curves()
                 StartWindow.close()
                 break
           
Start()
