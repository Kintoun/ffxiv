;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Globals ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;global ProcessName = FFXIVGAME
ProcessName = Notepad

INNER_QUIET = x
GREAT_STRIDES = q
STEADY_HAND = 4
INNOVATION = 8

PROGRESS = 1
QUALITY = e
	
NumIterations = 9999

;;;;;;;;;; Hotkeys ;;;;;;;;;;
; Press Ctrl+Alt+P to pause. Press it again to resume.
^!p::Pause
#MaxThreadsPerHotkey 3

^F12::
#MaxThreadsPerHotkey 1
ThreadProc("craft")
return

^F11::
#MaxThreadsPerHotkey 1
ThreadProc("mine")
return

;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Main ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;

ThreadProc(Action)
{
	global KeepRunning
	
	; If we're already running, then hotkey again means STOP
	if KeepRunning
	{
		SignalStop()
		return
	}
	KeepRunning := true
	Start(Action)
}

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;; Functions ;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Start(Action)
{	
	global KeepRunning, NumIterations
	
	Tooltip Starting script for %Action%
	Sleep 1000
	Tooltip

	Count = 0
	Loop %NumIterations%
	{
		Count++
		ToolTip Count=%Count%
		Sleep 500
		Tooltip
		
		DoOnce(Action)
		if not KeepRunning
			break
	}

	Tooltip Done
	Sleep 1000
	Tooltip
	KeepRunning := false
	return
}

DoOnce(Action)
{
	if Action = craft
	{
		Craft40(0)
	}
	else if Action = mine
	{
		Mine()
	}
	else
	{
		MsgBox "Unknown action: " . %Action%
	}
}

Mine()
{
	global KeepRunning
	
	SendToGame("{Numpad0}", 500)
}

Craft40(HQNum = 0)
{
	global KeepRunning
	
	StartSynthesis(HQNum)
	InnovationCraft(1)
	
	if KeepRunning
		Sleep 5000
}

InnovationCraft(SynthCount = 0)
{
	global
	
	SendToGame(INNER_QUIET, 1500)
	SendToGame(GREAT_STRIDES, 1500)
	SendToGame(STEADY_HAND, 1500)
	SendToGame(INNOVATION, 1500)
	
	SendToGame(QUALITY, 3500)
	SendToGame(GREAT_STRIDES, 1500)
	SendToGame(QUALITY, 3500)
	SendToGame(GREAT_STRIDES, 1500)
	SendToGame(QUALITY, 3500)
	
	Loop %SynthCount%
	{
		SendToGame(PROGRESS, 3500)
	}
}

StartSynthesis(HQNum = 0)
{
	SendToGame("{NumpadMult}", 500)
	SendToGame("{NumpadMult}", 500)
	SendToGame("{Numpad0}", 500)
	
	SetHQCount(HQNum)
}

SetHQCount(HQNum = 0)
{
	; TODO
}

SendToGame(KeyToSend, SleepTime)
{
	global ProcessName

	ControlSend,, %KeyToSend%, ahk_class %ProcessName%
	Sleep %SleepTime%
}

SignalStop()
{
	global KeepRunning
	
	KeepRunning := false
	Tooltip Stopping after this loop
	Sleep 1000
	Tooltip
}

/*
; AH notes
; Bracelets
	; Ziron nq
	; Spinel nq
; Ring
	; Spinel nq
; Earring
	; Zircon nq
	; Spinel nq
; Any
	; Amber
	; Turq
	; Tour
*/