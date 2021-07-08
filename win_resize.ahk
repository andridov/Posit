#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir c:\Home\Projects\Posit\  ; Ensures a consistent starting directory.

>#^3::
Run, pythonw win_resize.py -m 3x1
return

>#^4::
Run, pythonw win_resize.py -m 4x1
return

>#^5::
Run, pythonw win_resize.py -m 5x1
return


>#^e::
Run, pythonw win_resize.py -m 3x2
return

>#^r::
Run, pythonw win_resize.py -m 4x2
return

>#^t::
Run, pythonw win_resize.py -m 5x2
return



>#^a::
Run, pythonw win_resize.py -m 1x3
return

>#^s::
Run, pythonw win_resize.py -m 2x3
return

>#^d::
Run, pythonw win_resize.py -m 3x3
return

>#^f::
Run, pythonw win_resize.py -m 4x3
return

>#^g::
Run, pythonw win_resize.py -m 5x3
return


>#^z::
Run, pythonw win_resize.py -m 1x4
return

>#^x::
Run, pythonw win_resize.py -m 2x4
return

>#^c::
Run, pythonw win_resize.py -m 3x4
return

>#^v::
Run, pythonw win_resize.py -m 4x4
return

>#^b::
Run, pythonw win_resize.py -m 5x4
return
