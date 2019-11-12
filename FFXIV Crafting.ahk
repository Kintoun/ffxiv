;;;;;;;; Instructions ;;;;;;;
; HOW TO RUN:
; If ahk file association is setup, double click this script to launch it
; Control + F12 to open UI.
; Control + F12 when already running will stop a craft (same as Stop button)
; Select an item from the dropdown and click one of the buttons to start the script
; The script expects that you have your in-game crafting UI open (hotkey N) with the desired item selected
; Using HQ materials is not supported

; Actions:
; Do Once - Executes dropdown item once then stops.
; Repeat - Executes dropdown item inifitely.
; Pause - Pauses execution of the dropdown item. Click again to resume.
; Stop - Stops execution of the dropdown item.
; Run Simulation - Do Once in simulation mode. Will display commands in message box. If notepad is running commands will be sent there

; HOW TO ADD ITEMS TO DROPDOWN:
; Find DropDownList in the code below and add your item to the list
; In the section below labeled as "Crafts" make a new entry with the same name

; TODO:
; Add support for HQ materials

;;;;;;;;;; Hotkeys ;;;;;;;;;;
^F12::
#MaxThreadsPerHotkey 1

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Globals ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

ProcessName := "ffxiv_dx11.exe"
Simulation := false ; no need to set here, controlled via UI

class Action
{
	hotkey := "z"
	delay := 0
	
	__New(h, d)
	{
		this.hotkey := h
		this.delay := d
	}
}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;; Crafts ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Macros := {}
CraftMap := {}

; In-game Macros - waits and skills are handled in-game
; Action first parameter is hotkey, second parameter is summed waits in macro
Macros["Tofu Sugar Vinegar 1"] := new Action("7", 26000)
Macros["Tofu Sugar Vinegar 2"] := new Action("8", 19000)
Macros["Vinegar 1"] := new Action("7", 37000)
Macros["Vinegar 2"] := new Action("8", 6000)
Macros["Miso Dengaku 1"] := new Action("3", 38000)
Macros["Miso Dengaku 2"] := new Action("4", 17000)
Macros["Jhammel Moussaka 1"] := new Action("3", 38000)
Macros["Jhammel Moussaka 2"] := new Action("4", 20000)
Macros["Yaki Amberjack EggFoo 1"] := new Action("1", 38000)
Macros["Yaki Amberjack EggFoo 2"] := new Action("2", 17000)
Macros["Persimmon 1"] := new Action("3", 37000)
Macros["Persimmon 2"] := new Action("4", 29000)
Macros["Cottonseed Oil"] := new Action("5", 40000)
Macros["Pork Kakuni 1"] := new Action("7", 37000)
Macros["Pork Kakuni 2"] := new Action("8", 37000)

Macros["Infusion 1"] := new Action("1", 38000)
Macros["Infusion 2"] := new Action("2", 22000)

Macros["Kopp Nugget 1"] := new Action("1", 24000)
Macros["Kopp Nugget 2"] := new Action("2", 18000)
Macros["Kopp Ingot 2"] := new Action("2", 20000)
Macros["Kopp Ingot 2"] := new Action("5", 18000)

;CraftMap[""] := [" 1", " 2"]
CraftMap["Tofu Sugar Vinegar"] := ["Tofu Sugar Vinegar 1", "Tofu Sugar Vinegar 2"]
CraftMap["Vinegar"] := ["Vinegar 1", "Vinegar 2"]
CraftMap["Miso Dengaku"] := ["Miso Dengaku 1", "Miso Dengaku 2"]
CraftMap["Jhammel Moussaka"] := ["Jhammel Moussaka 1", "Jhammel Moussaka 2"]
CraftMap["Yaki Amberjack EggFoo"] := ["Yaki Amberjack EggFoo 1", "Yaki Amberjack EggFoo 2"]
CraftMap["Persimmon"] := ["Persimmon 1", "Persimmon 2"]
CraftMap["Cottonseed Oil"] := ["Cottonseed Oil"]
CraftMap["Pork Kakuni"] := ["Pork Kakuni 1", "Pork Kakuni 2"]
CraftMap["Infusion"] := ["Infusion 1", "Infusion 2"]

CraftMap["Kopp Nugget"] := ["Kopp Nugget 1", "Kopp Nugget 2"]
CraftMap["Kopp Ingot"] := ["Kopp Nugget 1", "Kopp Ingot 2"]
			
;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Main ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;

; If we're already running, then hotkey again means STOP
if KeepRunning
{
	SignalStop()
    return
}
KeepRunning := true
ShowDialog()

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Functions ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

ShowDialog()
{	
	global
	
	Gui, Add, DropDownList, vCraftChoice, Vinegar|Cottonseed Oil|Yaki Amberjack EggFoo|Miso Dengaku|Jhammel Moussaka|Persimmon|Kopp Nugget|Kopp Ingot|Infusion|Pork Kakuni
	Gui, Add, Button, default xm section, Do Once
	Gui, Add, Button, ys, Repeat
	Gui, Add, Button, ys, Pause
	Gui, Add, Button, ys, Stop
	Gui, Add, Button, ys, Run Simulation
	
	Gui, Show,, Crafting Helper
	return
	
	ButtonOK:
	ButtonDoOnce:
	Gui, Submit, NoHide
	Run(CraftChoice, 1)
	return
	
	ButtonRepeat:
	Gui, Submit, NoHide
	Run(CraftChoice, 9999)
	return
	
	ButtonRunSimulation:
	Gui, Submit, NoHide
	Run(CraftChoice, 1, true)
	return
	
	ButtonPause:
	Pause,,1
	return
	
	ButtonStop:
	SignalStop()
	return
	
	GuiClose:
	ExitApp
}

Run(CraftChoice, Iterations, RunSimulation = false)
{
	global
	
	if (Iterations < 1)
	{
		MsgBox % "Invalid parameters"
		return
	}

	KeepRunning := true
	Simulation := RunSimulation
	
	if (Simulation)
	{
		ProcessName := "notepad.exe"
	}
	else
	{
		ProcessName := "ffxiv_dx11.exe"
	}
	
	Tooltip Running
	Sleep 1000
	Tooltip
	
	Loop %Iterations%
	{
		DoOnce(CraftChoice)
		
		if Simulation or not KeepRunning
			break
		
		Sleep 7000

		if Simulation or not KeepRunning
			break
	}
	
	Tooltip Done
	Sleep 1000
	Tooltip
	KeepRunning := false
	return
}

DoOnce(CraftChoice)
{
	global KeepRunning, Simulation

	BasicCraft(CraftChoice)
}

BasicCraft(CraftChoice)
{
	global
	
	if (not Simulation)
	{
		StartSynthesis()
		Sleep 1500
	}
	
	Craft := CraftMap[CraftChoice]
	hotkeys := ""
	Loop % Craft.MaxIndex()
	{
		if KeepRunning
			hotkeys := hotkeys ExecuteAction(Craft[A_Index])
	}

	if (Simulation)
	{
		SendToGame("{Enter}", 100) ; newline for Notepad to separate simulations
		MsgBox % "Simulation complete: " hotkeys
	}
	
	return
}

StartSynthesis()
{
	; Confirm collectable
	;SendToGame("{Numpad0}", 1000)
	;SendToGame("{Numpad0}", 1000)

	; Send "UI confirm" messages to select item and start crafting process
	SendToGame("{Numpad0}", 750)
	SendToGame("{Numpad0}", 1000)
	SendToGame("{Numpad0}", 500)
	SendToGame("{Numpad0}", 500)

	SendToGame("{Numpad0}", 1000)	
}

SetHQCount(HQNum = 0)
{
	; Move cursor to ingredient column
	SendToGame("{Numpad8}", 500)
	SendToGame("{Numpad6}", 500)
	SendToGame("{Numpad6}", 500)
	
	; Hit up arrow for requested number of HQ ingredients
	Loop %HQNum%
	{
		SendToGame("{Numpad0}", 500)
	}
	
	SendToGame("{Numpad2}", 500)
}

ExecuteAction(name)
{
	global 
	
	Macro := Macros[name]
	
	if (Simulation)
	{
		SendToGame(Macro.hotkey, 100)
	}
	else
	{
		SendToGame(Macro.hotkey, Macro.delay)
	}
	
	return Macro.hotkey " <wait." Macro.delay ">"
}

SendToGame(KeyToSend, SleepTime)
{
	global ProcessName
	; ahk_exe searches by exe name e.g. Task Manager process name
	ControlSend,, %KeyToSend%, ahk_exe %ProcessName%
	Sleep %SleepTime%
}

SignalStop()
{
	global KeepRunning
	
	KeepRunning := false
	Tooltip Stopping after this loop
	Sleep 2000
	Tooltip
}